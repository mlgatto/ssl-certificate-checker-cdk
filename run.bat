@echo off

echo Executing the lambda handler

set DOMAINS=blog.xops.dev
python -c "import handler; handler.main(None, None)"
