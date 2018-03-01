from bots.core import CoreBot, EnableUtils
from bots.birthday import EnableBirthday
from bots.bug import EnableBugs
from bots.help import EnableHelp
from bots.ow import EnableOverwatch
from bots.party import EnableParties
from bots.poll import EnablePolls
from bots.cash import EnableCash
from bots.story import EnableStory
import discord
import asyncio
import random
random.seed()

"""Note:
This file is what we consider the 'reference implimentation' of Beymax.
bots/core.py and bots/utils.py contain the development framework upon which
all of Beymax is built. The remaining bots/*.py files build unique feature sets
out of this framework. This file is where we tie it all together. Starting from
the CoreBot (defined in bots/core.py) we add in a few additional just-for-fun
features (greetings, statuses, etc) which we wanted on our server, but which we didn't
think justified an entire feature set. Then we enable all of the other features
using EnableAll, and the various Enable___ functions. Lastly, the bot is launched
by reading a token out of token.txt

You are free to use any of the features in this file and others to get your bot
setup as you wish. Note that bots/help.py is considered server-specific and just
generally bad. We appologize and intend to deprecate or fix this code in the future

If you have any trouble, feel free to reach out to us by opening an issue on our
github repo https://github.com/agraubert/beymax
"""

def select_status():
    #return a randomly selected status message from the list
    return random.sample(
        [
            'Surgeon Simulator',
            'with himself',
            'the waiting game',
            'all of you for fools',
            'Big Hero 6: The Game',
            'Surgeon Simulator',
            'a robot doctor, but only on TV',
            'your loyal servant, for now',
            'with the server settings',
            'with the Discord API',
            'with your very lives',
            'Metadata Salesman'
        ],
        1
    )[0]


def ConstructBeymax(): #enable Beymax-Specific commands
    beymax = CoreBot()
    beymax = EnableStory(beymax) # Story needs priority on special message recognition

    @beymax.subscribe('after:ready')
    async def ready_up(self, event):
        print('Logged in as') #then run Beymax-Specific startup (print info)
        print(self.user.name)
        print(self.user.id)
        print('------')
        print("Bot connected to:")
        for server in self.servers:
            print(server.name)
        print("Bot has access to:")
        for channel in self.get_all_channels():
            print(channel.name, channel.type)
        print("Ready to serve!")
        self.dispatch('task:update_status') # manually set status at startup
        from bots.utils import Database
        async with Database('weekly.json') as weekly:
            print("Weekly xp structure:", weekly)

    @beymax.subscribe('member_join')
    async def greet_member(self, event, member): #greet new members
        await self.send_message(
            self.fetch_channel('general'),
            "Welcome, "+member.mention+"!\n"+
            "https://giphy.com/gifs/hello-hi-dzaUX7CAG0Ihi"
        )

    @beymax.add_command('!kill-beymax', '!satisfied')
    async def cmd_shutdown(self, message, content):
        """
        `!satisfied` : Shuts down beymax
        """
        await self.shutdown()

    @beymax.add_command('!_greet')
    async def cmd_greet(self, message, content):
        """
        `!_greet` : Manually triggers a greeting (I will greet you)
        """
        self.dispatch('member_join', message.author)

    @beymax.add_task(3600) # 1 hour
    async def update_status(self, *args):
        name = select_status()
        print("CHANGING STATUS:", name)
        await self.change_presence(
            game=discord.Game(name=name)
        )

    @beymax.add_command('!_status')
    async def cmd_status(self, message, content):
        if len(content[1:]):
            name = ' '.join(content[1:]).strip()
        else:
            name = select_status()
        await self.change_presence(
            game=discord.Game(name=name)
        )

    def pick(self, message):
        return random.random() < 0.05

    @beymax.add_special(pick)
    async def react(self, message, content):
        await self.add_reaction(
            message,
            b'\xf0\x9f\x91\x8d'.decode() if random.random() < 0.8 else b'\xf0\x9f\x8d\x86'.decode() # :thumbsup: and sometimes :eggplant:
        )
        # print("granting reaction xp")
        self.dispatch(
            'grant_xp',
            message.author,
            2
        )

    beymax.EnableAll( #enable all sub-bots
        EnableUtils,
        EnableBirthday,
        EnableBugs,
        EnableHelp,
        EnableOverwatch,
        EnableParties,
        EnablePolls,
        EnableCash,
    )

    return beymax

if __name__ == '__main__':
    with open("token.txt") as r:
        ConstructBeymax().run(r.read().strip())
