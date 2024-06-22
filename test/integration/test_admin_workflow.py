from unittest.mock import MagicMock
from datetime import datetime
from pycamp_bot.models import Pycamp, Pycampista, Slot
from pycamp_bot.commands import wizard
from test.conftest import use_test_database, test_db, MODELS
from pycamp_bot.commands import auth
from pycamp_bot.commands import voting
from pycamp_bot.commands import manage_pycamp
from pycamp_bot.commands import projects
from pycamp_bot.commands import wizard
from pycamp_bot.commands import base
from pycamp_bot.commands import raffle
from pycamp_bot.commands import schedule
from pycamp_bot.commands import announcements
from telegram.ext import Application, CommandHandler, ConversationHandler
import logging

LOGGER = logging.getLogger(__name__)


def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]


def setup_module(module):
    """setup any state specific to the execution of the given module."""
    test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
    test_db.connect()


def teardown_module(module):
    """teardown any state that was previously setup with a setup_module method."""
    # Not strictly necessary since SQLite in-memory databases only live
    # for the duration of the connection, and in the next step we close
    # the connection...but a good practice all the same.
    test_db.drop_tables(MODELS)

    # Close connection to db.
    test_db.close()
    # If we wanted, we could re-bind the models to their original
    # database here. But for tests this is probably not necessary.


class TestAdminWorkflow:

    def test_all_needed_commands_registered(self):
        application = Application.builder().token("1").build()

        auth.set_handlers(application)
        manage_pycamp.set_handlers(application)
        projects.set_handlers(application)
        voting.set_handlers(application)
        schedule.set_handlers(application)
        wizard.set_handlers(application)

        handlers = flatten_comprehension(
            [handler for handler in application.handlers.values()]
        )

        conversation_handlers_entry_points = flatten_comprehension(
            [
                handler._entry_points
                for handler in handlers
                if isinstance(handler, ConversationHandler)
            ]
        )

        commands = flatten_comprehension(
            [
                list(handler.commands)
                for handler in (handlers + conversation_handlers_entry_points)
                if isinstance(handler, CommandHandler)
            ]
        )

        """Login"""
        assert "su" in commands

        """configurar pycamp"""
        assert "empezar_pycamp" in commands
        assert "activar_pycamp" in commands
        assert "empezar_carga_proyectos" in commands
        assert "terminar_carga_proyectos" in commands
        assert "empezar_votacion_proyectos" in commands
        assert "terminar_votacion_proyectos" in commands
        assert "cronogramear" in commands
        assert "cambiar_slot" in commands

        """management de magos"""
        assert "agendar_magx" in commands
