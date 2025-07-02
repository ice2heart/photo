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
  }],

  deploy : {
    production : {
      user : 'ice',
      host : '192.168.1.225',
      ref  : 'origin/master',
      path : '~/photo/',
      repo : 'origin/master',
      'pre-deploy-local': '',
      'post-deploy' : 'cd photo_ui; npm install && pm2 reload ecosystem.config.js',
      'pre-setup': ''
    }
  }
};
