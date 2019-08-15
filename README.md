# yt-multiqueue-bot
A Streamlabs Chatbot script that enables using the Warp.World Multiqueue bot in Youtube chats.

This is really just a temporary script until Warp World releases official support for youtube (currently in progress). Once Youtube is officially supported, I won't be maintaining this any longer.

# Installation

1. Download the .zip file using the green button to the upper right
2. Extract the "yt-multiqueue-bot-master" folder into `Streamlabs Chatbot\Services\Scripts`
3. Open Streamlabs Chat Bot, navigate to the `</> Scripts` tab. If the Scripts tab isn't present, please refer to https://github.com/StreamlabsSupport/Streamlabs-Chatbot/wiki/Prepare-&-Import-Scripts
4. Find the script named YT Multiqueue Bot, click on it and fill in the appropiate settings
5. Hit the "Enable" checkbox after saving settings, or turn it off then back on again to ensure the new settings have been loaded.
6. Use the !queue command in your chat to test, it will display the name of the current queue

# Commands

The commands are largely copied from the offical commands. Editing your commands on warp world will edit them on the Youtube bot. The major difference is the response for the !current command which is hard coded into this bot.

There is no support for detecting if a user is a subscriber (equal to Twitch follower) so any commands related to followers will not work. However all the subscriber commands like !subrandom and !subnext should work on Youtube for Sponsors (equal to twitch subscribers)

There is also one added command which uses StreamLabs Chatbot active user detection, !nextactive will find the next queue entry that has been made by a recently active viewer in chat. It only supports queue entries made from youtube.

