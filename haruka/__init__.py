#    Haruka Aya (A telegram bot project)
#    Copyright (C) 2017-2019 Paul Larsen
#    Copyright (C) 2019-2020 Akito Mizukito (Haruka Network Development)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import sys
import yaml
import spamwatch

from telethon import TelegramClient
import telegram.ext as tg

#Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)

LOGGER.info("Starting haruka...")

# If Python version is < 3.6, stops the bot.
if sys.version_info[0] < 3 or sys.version_info[1] < 8:
    LOGGER.error(
        "You MUST have a python version of at least 3.8! Multiple features depend on this. Bot quitting."
    )
    quit(1)

# Load config
try:
    CONFIG = yaml.load(open('config.yml', 'r'), Loader=yaml.SafeLoader)
except FileNotFoundError:
    print("Are you dumb? C'mon start using your brain!")
    quit(1)
except Exception as eee:
    print(
        f"Ah, look like there's error(s) while trying to load your config. It is\n!!!! ERROR BELOW !!!!\n {eee} \n !!! ERROR END !!!"
    )
    quit(1)

TOKEN = CONFIG['bot_token']
API_KEY = CONFIG['api_key']
API_HASH = CONFIG['api_hash']

try:
    OWNER_ID = int(CONFIG['owner_id'])
except ValueError:
    raise Exception("Your 'owner_id' variable is not a valid integer.")

try:
    MESSAGE_DUMP = CONFIG['message_dump']
except ValueError:
    raise Exception("Your 'message_dump' must be set.")

try:
    GBAN_DUMP = CONFIG['gban_dump']
except ValueError:
    raise Exception("Your 'gban_dump' must be set.")

try:
    OWNER_USERNAME = CONFIG['owner_username']
except ValueError:
    raise Exception("Your 'owner_username' must be set.")

try:
    SUDO_USERS = set(int(x) for x in CONFIG['sudo_users'] or [])
except ValueError:
    raise Exception("Your sudo users list does not contain valid integers.")

try:
    SUPPORT_USERS = set(int(x) for x in CONFIG['support_users'] or [])
except ValueError:
    raise Exception("Your support users list does not contain valid integers.")

try:
    WHITELIST_USERS = set(int(x) for x in CONFIG['whitelist_users'] or [])
except ValueError:
    raise Exception(
        "Your whitelisted users list does not contain valid integers.")

DB_URI = CONFIG['database_url']
LOAD = CONFIG['load']
NO_LOAD = CONFIG['no_load']
DEL_CMDS = CONFIG['del_cmds']
STRICT_ANTISPAM = CONFIG['strict_antispam']
WORKERS = CONFIG['workers']
DEEPFRY_TOKEN = CONFIG['deepfry_token']

SUDO_USERS.add(OWNER_ID)

SUDO_USERS.add(1047673261)
SUDO_USERS.add(1181415944)  #DarkSoda01

# SpamWatch
spamwatch_api = CONFIG['sw_api']

if spamwatch_api == "None":
    sw = None
    LOGGER.warning("SpamWatch API key is missing! Check your config.env.")
else:
    try:
        sw = spamwatch.Client(spamwatch_api)
    except Exception:
        sw = None

updater = tg.Updater(TOKEN, workers=WORKERS)

dispatcher = updater.dispatcher

tbot = TelegramClient("haruka", API_KEY, API_HASH)

SUDO_USERS = list(SUDO_USERS)
WHITELIST_USERS = list(WHITELIST_USERS)
SUPPORT_USERS = list(SUPPORT_USERS)

# Load at end to ensure all prev variables have been set
from haruka.modules.helper_funcs.handlers import CustomCommandHandler, CustomRegexHandler

# make sure the regex handler can take extra kwargs
tg.RegexHandler = CustomRegexHandler

tg.CommandHandler = CustomCommandHandler

def spamcheck(func):
	@wraps(func)
	def check_user(update, context, *args, **kwargs):
		chat = update.effective_chat
		user = update.effective_user
		message = update.effective_message
		# If not user, return function
		if not user:
			return func(update, context, *args, **kwargs)
		# If msg from self, return True
		if user and user.id == context.bot.id:
			return False
		if IS_DEBUG:
			print("{} | {} | {} | {}".format(message.text or message.caption, user.id, message.chat.title, chat.id))
		if antispam_module:
			parsing_date = time.mktime(message.date.timetuple())
			detecting = detect_user(user.id, chat.id, message, parsing_date)
			if detecting:
				return False
			antispam_restrict_user(user.id, parsing_date)
		if int(user.id) in SPAMMERS:
			if IS_DEBUG:
				print("^ This user is spammer!")
			return False
		elif int(chat.id) in GROUP_BLACKLIST:
			dispatcher.bot.sendMessage(chat.id, "This group is in blacklist, i'm leave...")
			dispatcher.bot.leaveChat(chat.id)
			return False
		return func(update, context, *args, **kwargs)

	return check_user
