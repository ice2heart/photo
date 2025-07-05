module.exports = {
  apps : [{
    name   : "backend",
    watch: false,
    script : "./app.py",
    interpreter : "python3",
    interpreter_args : "-m fastapi dev"
  },
  {
    name   : "frontend",
    watch: false,
    cwd   : "./photo_ui/",
    exec_mode: 'fork',
    instances: '1', // Or a number of instances
    script: 'node_modules/next/dist/bin/next',
    args: 'dev'
  }]
};
