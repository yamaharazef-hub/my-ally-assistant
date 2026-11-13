#!/bin/sh
cd $(dirname $0)
cd ..
source env/bin/activate
cd allycli
pydocmd simple CmdInterpreter CmdInterpreter.AllyAPI+ > ../doc/API.md
pydocmd simple tests tests.PluginTest+ tests.MockHistory+ > ../doc/TEST_API.md
