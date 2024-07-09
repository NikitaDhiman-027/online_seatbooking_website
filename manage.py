from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db  # Assuming app and db are defined in app.py

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
