import http.client
import json
import threading
import unittest
from unittest.mock import patch

import app


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = app.ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.server.token = 'test-token'
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.origin = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        result = response.status, response.read()
        conn.close()
        return result

    def test_home_and_status(self):
        status, body = self.request('GET', '/')
        self.assertEqual(status, 200)
        self.assertIn(b'What', body)
        status, body = self.request('GET', '/api/status')
        self.assertEqual(json.loads(body)['token'], 'test-token')
        self.assertEqual(status, 200)

    def test_rejects_bad_host_and_cross_origin(self):
        status, _ = self.request('GET', '/', headers={'Host': 'attacker.example'})
        self.assertEqual(status, 403)
        status, _ = self.request('POST', '/api/chat', '{}', {'Origin': 'https://evil.example', 'X-Ally-Token': 'test-token'})
        self.assertEqual(status, 403)
        status, _ = self.request('POST', '/api/chat', '{}', {'Origin': self.origin, 'X-Ally-Token': 'wrong'})
        self.assertEqual(status, 403)

    @patch('app.chat', return_value='Ready to help!')
    @patch('app.settings', return_value={'key': 'test-key', 'model': 'test-model'})
    def test_chat_and_invalid_messages(self, settings, chat):
        headers = {'Origin': self.origin, 'X-Ally-Token': 'test-token', 'Content-Type': 'application/json'}
        body = json.dumps({'messages': [{'role': 'user', 'content': 'Hello'}]})
        status, result = self.request('POST', '/api/chat', body, headers)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(result)['reply'], 'Ready to help!')
        chat.assert_called_once_with([{'role': 'user', 'content': 'Hello'}], {'key': 'test-key', 'model': 'test-model'})
        status, _ = self.request('POST', '/api/chat', json.dumps({'messages': [{'role': 'system', 'content': 'no'}]}), headers)
        self.assertEqual(status, 400)

    @patch('app.settings', return_value={'key': '', 'model': 'test-model'})
    def test_missing_key(self, settings):
        headers = {'Origin': self.origin, 'X-Ally-Token': 'test-token'}
        status, result = self.request('POST', '/api/chat', json.dumps({'messages': [{'role': 'user', 'content': 'Hi'}]}), headers)
        self.assertEqual(status, 503)
        self.assertIn('not configured', json.loads(result)['error'])

class ProviderTests(unittest.TestCase):
    @patch('app.urllib.request.urlopen')
    def test_arena_request(self, urlopen):
        import io
        urlopen.return_value.__enter__.return_value = io.BytesIO(json.dumps({'choices': [{'message': {'content': 'Hello!'}}]}).encode())
        self.assertEqual(app.chat([{'role': 'user', 'content': 'Hi'}], {'key': 'secret', 'model': 'my-model'}), 'Hello!')
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, 'https://api.arena.ai/v1/chat/completions')
        self.assertEqual(request.get_header('Authorization'), 'Bearer secret')
        self.assertEqual(payload['model'], 'my-model')
        self.assertEqual(payload['messages'][0]['role'], 'system')
        self.assertEqual(payload['messages'][-1]['content'], 'Hi')


if __name__ == '__main__':
    unittest.main()
