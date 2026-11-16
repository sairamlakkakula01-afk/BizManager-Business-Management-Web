import os
import getpass
import click
from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.settings import BusinessSettings

# Initialize the Flask application using environment or default
env_name = os.environ.get('FLASK_ENV', 'development')
app = create_app('development' if env_name == 'development' else 'production')


@app.cli.command("init-db")
def init_db():
    """Create database tables and ensure business settings are initialized."""
    with app.app_context():
        db.create_all()
        BusinessSettings.get_settings()
        click.echo(click.style("✓ Database tables and default settings initialized successfully.", fg="green"))


@app.cli.command("create-admin")
@click.option("--username", prompt=True, help="Administrator username")
@click.option("--email", prompt=True, help="Administrator email address")
@click.option("--full-name", prompt=True, default="System Administrator", help="Administrator full name")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Administrator password")
def create_admin(username, email, full_name, password):
    """Safely create an initial administrator account with secure password hashing."""
    with app.app_context():
        db.create_all()
        # Verify if username or email already exists
        if User.query.filter_by(username=username.strip()).first():
            click.echo(click.style(f"Error: User with username '{username}' already exists.", fg="red"))
            return
        if User.query.filter_by(email=email.strip().lower()).first():
            click.echo(click.style(f"Error: User with email '{email}' already exists.", fg="red"))
            return

        if len(password) < 8:
            click.echo(click.style("Error: Password must be at least 8 characters long.", fg="red"))
            return

        admin = User(
            username=username.strip(),
            email=email.strip().lower(),
            full_name=full_name.strip(),
            role=Role.ADMIN,
            is_active=True
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        click.echo(click.style(f"✓ Administrator account '{admin.username}' ({admin.email}) created successfully!", fg="green"))


@app.cli.command("seed-demo")
def seed_demo():
    """Populate database with realistic business sample data for testing and demonstrations."""
    from scripts.seed_data import run_seed
    with app.app_context():
        run_seed()


if __name__ == '__main__':
    import sys
    # If a CLI command is provided like 'init-db' or 'create-admin', dispatch to Flask CLI
    if len(sys.argv) > 1 and sys.argv[1] not in ('run', '--help'):
        app.cli()
    else:
        port = int(os.environ.get('PORT', 5050))
        app.run(host='127.0.0.1', port=port, debug=True)

