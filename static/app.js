'use strict';
const $ = (selector) => document.querySelector(selector);
const input = $('#input'), conversation = $('#conversation'), welcome = $('#welcome'), feedback = $('#feedback'), send = $('#send');
const STORAGE = 'ally-conversation-v1';
let messages = [], token = '', busy = false, speaking = false, recognition = null;
try { const saved = JSON.parse(localStorage.getItem(STORAGE) || '[]'); if (Array.isArray(saved)) messages = saved.filter(m => m && ['user','assistant'].includes(m.role) && typeof m.content === 'string').slice(-30); } catch (_) {}
function save() { try { localStorage.setItem(STORAGE, JSON.stringify(messages)); } catch (_) { feedback.textContent = 'Conversation could not be saved in this browser.'; } }
function render() {
  conversation.replaceChildren(); welcome.hidden = messages.length > 0; conversation.hidden = messages.length === 0;
  for (const m of messages) {
    const item = document.createElement('div'); item.className = 'message ' + m.role;
    const label = document.createElement('span'); label.className = 'role'; label.textContent = m.role === 'user' ? 'YOU' : 'ALLY';
    item.append(label, document.createTextNode(m.content)); conversation.append(item);
  }
  if (busy) { const pending = document.createElement('div'); pending.className = 'message pending'; pending.textContent = 'Ally is thinking…'; conversation.append(pending); }
  conversation.scrollTop = conversation.scrollHeight;
}
async function status() {
  try { const response = await fetch('/api/status'); if (!response.ok) throw Error(); const data = await response.json(); token = data.token;
    $('#status span').textContent = data.configured ? 'API key configured' : 'Setup required'; $('#status').classList.toggle('unconfigured', !data.configured);
    if (!data.configured) feedback.textContent = 'Run ./scripts/setup.py to add your Arena API key, then restart Ally.';
  } catch (_) { $('#status span').textContent = 'Server unavailable'; $('#status').classList.add('unconfigured'); }
}
async function submit(text) {
  text = text.trim(); if (!text || busy) return;
  feedback.textContent = ''; input.value = ''; input.style.height = 'auto'; busy = true; send.disabled = true;
  messages.push({role: 'user', content: text}); render();
  try {
    const response = await fetch('/api/chat', {method:'POST', headers:{'Content-Type':'application/json', 'X-Ally-Token':token}, body: JSON.stringify({messages: messages.slice(-30)})});
    const data = await response.json(); if (!response.ok) throw new Error(data.error || 'Something went wrong.');
    messages.push({role:'assistant', content:data.reply}); messages = messages.slice(-30); save();
    if (speaking && 'speechSynthesis' in window) { speechSynthesis.cancel(); speechSynthesis.speak(new SpeechSynthesisUtterance(data.reply)); }
  } catch (error) { messages.pop(); input.value = text; feedback.textContent = error.message || 'Could not connect to Ally.'; }
  finally { busy = false; send.disabled = false; render(); }
}
send.addEventListener('click', () => submit(input.value));
input.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); submit(input.value); } });
input.addEventListener('input', () => { input.style.height = 'auto'; input.style.height = Math.min(input.scrollHeight, 160) + 'px'; });
document.querySelectorAll('.suggestion').forEach(button => button.addEventListener('click', () => submit(button.dataset.prompt)));
$('#new-chat').addEventListener('click', () => { if (busy) { feedback.textContent = 'Wait for the current response before starting a new conversation.'; return; } if (messages.length && !confirm('Clear this conversation from this browser?')) return; messages = []; save(); if ('speechSynthesis' in window) speechSynthesis.cancel(); feedback.textContent = ''; render(); input.focus(); });
$('#sound').addEventListener('click', () => { if (!('speechSynthesis' in window)) { feedback.textContent = 'Spoken replies are not supported by this browser.'; return; } speaking = !speaking; $('#sound').setAttribute('aria-pressed', String(speaking)); $('.sound-label').textContent = speaking ? 'Voice on' : 'Voice off'; if (!speaking) speechSynthesis.cancel(); });
const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (Recognition) {
  recognition = new Recognition(); recognition.lang = navigator.language || 'en-US'; recognition.interimResults = false;
  recognition.onstart = () => { $('#mic').classList.add('listening'); $('#mic').setAttribute('aria-label', 'Stop voice input'); feedback.textContent = 'Listening…'; };
  recognition.onresult = e => { input.value = (input.value ? input.value + ' ' : '') + e.results[0][0].transcript; feedback.textContent = 'Review your message, then press send.'; input.focus(); };
  recognition.onerror = e => { feedback.textContent = 'Voice input: ' + e.error + '. Check microphone permission and browser support.'; };
  recognition.onend = () => { $('#mic').classList.remove('listening'); $('#mic').setAttribute('aria-label', 'Start voice input'); if (feedback.textContent === 'Listening…') feedback.textContent = ''; };
}
$('#mic').addEventListener('click', () => { if (!recognition) { feedback.textContent = 'Voice input is unavailable here. Try Chrome or Chromium with microphone permission.'; return; } try { if ($('#mic').classList.contains('listening')) recognition.stop(); else recognition.start(); } catch (_) { feedback.textContent = 'Could not start voice input. Check microphone permission.'; } });
render(); status();
