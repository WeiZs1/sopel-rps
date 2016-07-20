'''
rock-paper-scissors module for sopel irc bot
(Probably) Copyright WZ1 2016
'''
from sopel import module,tools
from random import choice
import time

#cooldown between games of RPS in seconds
COOLDOWN = 30

#Editable strings for people who don't appreciate my mastery of bad tropes.
STRINGS = {
    'WIN':              ["It's not like I lost for you, %s!",
                         "It seems luck is on your side, %s. I'll get you eventually, I swear!"],
    'LOSS':             ["Sorry! It's not like I meant to win, %s. I swear!",
                         "Looks like your luck has taken a turn for the worse, %s. Maybe next time?"],
    'TIE':              ["Looks like it's a tie, %s!"]
}
#Options ordered so that the next in the list beats the previous.
OPTIONS=['rock','paper','scissors']

@module.commands('rps')
def rps(bot, trigger):
    global OPTIONS
    if not trigger.group(3) or trigger.group(3) not in OPTIONS:
        bot.say("Try picking an option from the following: rock, paper, scissors")
        return module.NOLIMIT
    playersel=trigger.group(3).lower()
    time_since = time_since_last_rps(bot, trigger.nick)
    if time_since < COOLDOWN:
        bot.notice("You must wait %d seconds until our next game of RPS." % ( COOLDOWN- time_since), trigger.nick)
        return module.NOLIMIT
    botsel=choice(OPTIONS)
    bot.say("%s vs %s..." % (playersel, botsel))
    if botsel==playersel:
        bot.say(choice(STRINGS['TIE']) % trigger.nick)
        update_stats(bot, trigger.nick , 0)
    elif OPTIONS.index(botsel)-1 == OPTIONS.index(playersel):
        bot.say(choice(STRINGS['LOSS']) % trigger.nick)
        update_stats(bot, trigger.nick,-1)
    else:
        bot.say(choice(STRINGS['WIN']) % trigger.nick)
        update_stats(bot, trigger.nick,1)
    wins,losses,ties = get_stats(bot,trigger.nick)
    bot.say('Your stats are: \x0304%d\x03 wins, \x0304%d\x03 losses, \x0304%d\x03 ties.' % (wins, losses, ties))
    bot.db.set_nick_value(trigger.nick, 'rps_last', time.time())
    
def get_stats(bot, nick):
    wins = bot.db.get_nick_value(nick, 'rps_wins') or 0
    losses = bot.db.get_nick_value(nick, 'rps_losses') or 0
    ties = bot.db.get_nick_value(nick, 'rps_ties') or 0
    return wins, losses, ties

def update_stats(bot, nick, won=0):
    wins, losses, ties = get_stats(bot,nick)
    if won == -1:
        bot.db.set_nick_value(nick, 'rps_losses',losses+1)
    if won == 0:
        bot.db.set_nick_value(nick, 'rps_ties',ties+1)
    if won == 1:
        bot.db.set_nick_value(nick, 'rps_wins',wins+1)

def time_since_last_rps(bot, nick):
    now = time.time()
    last = bot.db.get_nick_value(nick, 'rps_last') or 0
    return abs(now - last)
