from telethon import TelegramClient,events,custom,Button,functions
from telethon.errors import UserNotParticipantError, ChannelPrivateError, MessageIdInvalidError,FloodWaitError
from telethon.tl.types import PeerUser,PeerChannel
from asyncio import sleep
from json import loads
from Database.Database import Database
import logging
logging.basicConfig(filename="log.txt", filemode="a+", format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)
Data = dict(loads(open('Database/Config.json','r').read()))
AllPost = {}
SleepForDelPost = 8
# --------------------------------------------------- Config ------------------------------------------------------------
UserNameBot = 'MohamamdMahdiArbabpouri'  # bot UserName without @ example: telegrambot
Creator = [2056493966, ] # creators user id
ApiID = 123456789 # Api ID
ApiHash = '' # Api Hash
Token = '' # Token Bot
Bot = TelegramClient('Bot', ApiID, ApiHash).start(bot_token=Token)
# ----------------------------------------------------- Bot --------------------------------------------------------------
async def main():
    try:
        async def StartMenu(UserID, Text):
            global Send
            if UserID in Creator:
                ButtonCR = [
                    [Button.inline('👤 آمار ربات 👤', 'Members')],
                    [Button.inline('🗣 ارسال همگانی 🗣', 'SendToAll')],
                    [Button.inline('🗂 ReStart 🗂', 'Data')],
                    [Button.inline('✅ اضافه کردن قفل ✅', 'AddChannel'), Button.inline('❌ حذف چنل ❌', 'RemoveChannel')],
                    [Button.inline('🗄 لیست چنل ها 🗄', 'ChannelList')],
                    [Button.inline('🔓 اضافه کردن ادمین 🔓', 'AddAdmin'), Button.inline('🔒 حذف ادمین 🔒', 'DelAdmin')],
                    [Button.inline('🗄 لیست ادمین ها 🗄', 'AdminsList')],
                    [Button.inline('📍 بستن پنل 📍', 'Close')]
                ]
                Send = await Bot.send_message(UserID, Text, buttons=ButtonCR)
            elif UserID in Data['Admins']:
                ButtonAdmin = [
                    [Button.inline('👤 آمار ربات 👤', 'Members')],
                    [Button.inline('📍 بستن پنل 📍', 'Close')]
                ]
                Send = await Bot.send_message(UserID, Text, buttons=ButtonAdmin)

        async def ForcedToJoin(UserID):
            if Data['ChannelsID'] == []:
                return True
            Check = 0
            NoJoin = []

            for i, ii in zip(Data['ChannelsID'], Data['ChannelsLink']):
                try:
                    ChannelInfo = await Bot.get_entity(PeerChannel(int(i)))
                    ChannelsFull = await Bot(functions.channels.GetParticipantRequest(ChannelInfo, UserID))
                    Check += 1
                    if Check == len(Data['ChannelsID']):
                        return True

                except UserNotParticipantError:
                    NoJoin.append(ii)
            if NoJoin != []:
                Num = 1
                ButtonList = []
                for i in NoJoin:
                    ButtonList.append([Button.url(f"🔆 Channel {Num} ❤️‍🔥", url=i)])
                    Num += 1
                ButtonList.append([Button.inline("جوین شدم ❣️ | دریافت ویدیو 💚", "CheckJoin")])
                await Bot.send_message(PeerUser(UserID),'** سلام دوست من , برای استفاده از ربات باید عضو کانال های زیر بشی بعد روی جوین شدم کلیک کن تا ویدیو برات ارسال شه 🤍 **',buttons=ButtonList)

        def CheckCreator(event):
            if event.is_private:
                if event.sender_id in Creator:
                    return True
                else:
                    return False

        def AdAndCr(event):
            if event.is_private:
                if event.sender_id in Data['Admins'] or event.sender_id in Creator:
                    return True
                else:
                    return False

        async def SendToAll(Message,Admin):
            await RefreshDataFunc()
            Num = 0
            for i in Data['Users']:
                try:
                    await Bot.send_message(PeerUser(i), Message)
                    Num += 1
                except Exception as ex:
                    print(str(ex))
            await Bot.send_message(PeerUser(Admin), (f'**⚜️ Sended 🪄 : To {str(Num)} Members ✅ **'))

        
        @Bot.on(events.NewMessage(func=AdAndCr, pattern='/panel'))
        async def AdminPanel(event: custom.message.Message):
            await StartMenu(event.sender_id, '**♻️ Welcome To Panel ♻️**')

        @Bot.on(events.CallbackQuery(data='Members', func=AdAndCr))
        async def UsersInBot(event: events.CallbackQuery.Event):
            await RefreshDataFunc()
            await event.reply(f'**🧿 Amar Bot Shoma Ta In Lahze : {len(Data["Users"])} Mibashad ☄️**')

        @Bot.on(events.CallbackQuery(data='SendToAll', func=CheckCreator))
        async def SendMessageToAll(event: events.CallbackQuery.Event):
            await event.reply('**🔋 Payam (Video,Voice,Text,...) Khod Ra Ersal Konid , Baraye Cancel Kardan : /cancel or /start or /panel 📍**')
            @Bot.on(events.NewMessage(func=CheckCreator))
            async def GetMessageForSendToAll(event2: custom.message.Message):
                if event.sender_id == event2.sender_id:
                    Message = event2.message
                    if Message.message in ['/start', '/cancel', '/panel']:
                        await StartMenu(event2.sender_id,'**🤖 Canceled , Welcome Back 🤖**')
                        Bot.remove_event_handler(GetMessageForSendToAll)
                    else:
                        Bot.remove_event_handler(GetMessageForSendToAll)
                        await event2.reply(f'**⏳️ Sabr Kon Ta Payam Ro Baraye {len(Data["Users"])} Nafar Befrestam ⌛️**')
                        await SendToAll(Message,event2.sender_id)


        @Bot.on(events.CallbackQuery(data='AddChannel', func=CheckCreator))
        async def AddLockChannel(event: events.CallbackQuery.Event):
            await event.reply('**🤖 : Ebteda Man Ro Dakhel Channel Mad Nazar Admin Kon Sepas Yek Payam Az Channel Baram Forward Kon 🤠\nBaraye Cancel Kardan : /cancel or /start or /panel 📍**')
            @Bot.on(events.NewMessage(func=CheckCreator))
            async def GetChannel(event2: custom.message.Message):
                if event.sender_id == event2.sender_id:
                    try:
                        if event2.raw_text in ['/start', '/cancel', '/panel']:
                            await StartMenu(event2.sender_id,'**  🟢 Closed , Welcome Back  🟢**')
                            Bot.remove_event_handler(GetChannel)
                        elif event2.forward.is_channel:
                            ChannelInfo = await Bot.get_entity(event2.fwd_from.from_id.channel_id)
                            ChannelInfo2 = await Bot(functions.channels.GetFullChannelRequest(ChannelInfo))
                            if ChannelInfo.id not in Data['ChannelsID']:
                                Bot.remove_event_handler(GetChannel)
                                Link = ChannelInfo2.full_chat.exported_invite.link
                                Database(Select='Add', ChannelID=ChannelInfo.id, ChannelLink=Link,Data=Data).RefreshChannel()
                                await RefreshDataFunc()
                                await event2.reply(f'**♥️ Channel Set Shod : {Link} 👽**')
                                ChannelInfo = 0
                            else:
                                await event2.reply('**❌ In Channel Ghablan Sabt Shode , Mojadad Emtehan Kodin\nBaraye Cancel Kardan : /cancel or /start or /panel 📍 **')
                        else:
                            await event2.reply('** ⚠️Lotfan Payam Ru Az Channel Forward Kon Na Jaye Dige ‼ \nBaraye Cancel Kardan : /cancel or /start or /panel 📍️ **')
                    except ChannelPrivateError:
                        await event2.reply('** ⭕️Avval Bayad Adminam Koni Bad Forward Koni :(  ⭕\nBaraye Cancel Kardan : /cancel or /start or /panel 📍️**')
                    except AttributeError:
                        await event2.reply('** ⚠️ Moshkeli Pish Omad , Ebteda Mano Admin Kon va Tik Hamu Bede , Bad Payam Ro Forward Kon ✅\nBaraye Cancel Kardan : /cancel or /start or /panel 📍 **')
                    else:
                        await event2.reply(f'Creator Aziz Goya Moshkeli Pish Amade. \n1) Ckeck Kon Bebin Admin Kardi Ya Na\n2)Tik Haye Adminiru Bishtar Kon(Tik Edit Channel Va Add Member)\nMatn Error: \n{str(ex)}\n\nBaraye Cancel Kardan : /cancel or /start or /panel 📍')

        @Bot.on(events.CallbackQuery(data='RemoveChannel', func=CheckCreator))
        async def RemoveChannelLock(event: events.CallbackQuery.Event):
            Channels = ""
            Num = -1
            for i, ii in zip(Data['ChannelsLink'], Data['ChannelsID']):
                Num += 1
                Channels += (f'{str(Num+1)}) {str(i)} : ID = {ii}\n\n')
            await event.reply(f'** 🔰 Lotfan ID Channel Ro Vared Kon Ta Deletesh Konam ⁉️\n{Channels}\n\nBaraye Cancel Kardan : /cancel or /start or /panel 📍**')
            Channels = 0
            @Bot.on(events.NewMessage(func=CheckCreator))
            async def GetLinkForDelChannel(event2: custom.message.Message):
                if event.sender_id == event2.sender_id:
                    Text = event2.raw_text
                    if Text in str(Data['ChannelsID']):
                        Number = -1
                        for i in Data['ChannelsID']:
                            Number += 1
                            if str(i) == str(Text):
                                break
                        CHLink, CHID = Data['ChannelsLink'][Number], Data['ChannelsID'][Number]
                        await StartMenu(event2.sender_id, f"** 🔴 Link : {CHLink} , ID : {CHID} Deleted ❌ **")
                        Database(Select='Remove', ChannelLink=CHLink, ChannelID=CHID,Data=Data).RefreshChannel()
                        await RefreshDataFunc()
                        CHLink, CHID = 0, 0
                        Bot.remove_event_handler(GetLinkForDelChannel)
                    elif event2.message.message in ['/start', '/panel','/cancel']:
                        Bot.remove_event_handler(GetLinkForDelChannel)
                        await StartMenu(event2.sender_id, '** ♥️ Back To Menu ✅ **')
                    else:
                        await event.reply('** ID Ersal shode eshtebah Ghorban 🤡, 🔺Jahast Cancel kardan amaliyat : /cancel or /start or /panel 🫡**')

        @Bot.on(events.CallbackQuery(data='ChannelList', func=CheckCreator))
        async def ListChannel(event: events.CallbackQuery.Event):
            Channels = ""
            Num = 0
            for i in Data['ChannelsLink']:
                Num += 1
                Channels += (f'{str(Num)}) {str(i)} 🛠\n\n')
            await event.reply(f'**⚙️ Channels List : \n{Channels} **')
            Channels = 0

        @Bot.on(events.CallbackQuery(data='AddAdmin', func=CheckCreator))
        async def AddAdmin(event: events.CallbackQuery.Event):
            await event.reply('** 🆔 Lotfan ID Adadi Admin Ra Ersal Konid  ⁉️\nBaraye Cancel Kardan : /cancel or /start or /panel**')
            @Bot.on(events.NewMessage(func=CheckCreator))
            async def GiveUserIDAdmin(event2: custom.message.Message):
                if event.sender_id == event2.sender_id:
                    Text = event2.raw_text
                    if Text.isnumeric():
                        if int(Text) in Creator:
                            await StartMenu(event2.sender_id,'** Panel Closed\n❌ Ishan Az Sazandegan Hastand Nemitavan Adminesh Kard ❌**')
                            Bot.remove_event_handler(GiveUserIDAdmin)
                        elif int(Text) not in Data['Admins']:
                            Database(Select='Add', UserID=int(Text),Data=Data).RefreshAdmin()
                            await RefreshDataFunc()
                            await StartMenu(event2.sender_id,'**✅Admin Add Shod✅**')
                            Bot.remove_event_handler(GiveUserIDAdmin)
                        else:
                            await event2.reply('**⚠️ Ishan Dar List Admin Ha Hozur Darand ♻\n\nBaraye Cancel Kardan : /cancel or /start or /panel 📍**')
                    elif event2.message.message in ['/start','/cancel','/panel']:
                        await StartMenu(event2.sender_id, '**Canceled\nWelcome Back ✅ **')
                        Bot.remove_event_handler(GiveUserIDAdmin)
                    else:
                        await event2.reply('**🚫 Meghdar Vared Shode Nadorost Ast , Mojadad Talash Konid\nJahast Cancel Kardan : /start or /panel or /cancel ⛔️**')

        @Bot.on(events.CallbackQuery(data='DelAdmin', func=CheckCreator))
        async def RemoveAdmin(event: events.CallbackQuery.Event):
            Admins, Num = '', 0
            for i in Data['Admins']:
                Num += 1
                Admins += f"{Num}) {str(i)}🫡 \n"
            await event.reply(f'** 🆔 Lotfan ID Adadi Admin Ra Ersal Konid Ta Sikeshu Bezanam ⁉\n{Admins}\nBaraye Cancel Kardan : /cancel or /start or /panel**')

            @Bot.on(events.NewMessage(chats=event.chat_id))
            async def GetUserAdminForDel(event2: custom.message.Message):
                Text = event2.raw_text
                if Text.isnumeric():
                    if int(Text) in Data['Admins']:
                        Bot.remove_event_handler(GetUserAdminForDel)
                        Database(Select='Remove', UserID=int(Text),Data=Data).RefreshAdmin()
                        await event.reply('** Admin Deleted  ✅**')
                        await RefreshDataFunc()
                    else:
                        await event2.reply('** Ishan Dar List Admin Ha Hozor Nadarad ⁉ \n\nBaraye Cancel Kardan : /cancel or /start or /panel 📍️**')
                elif event2.message.message in ['/start', '/cancel', '/panel']:
                    Bot.remove_event_handler(GetUserAdminForDel)
                    await StartMenu(event2.sender_id, '** Canceled\nWelcome Back 🟢**')
                else:
                    await event2.reply('**🚫 Meghdar Vared Shode Nadorost Ast Mojadad Talash Konid\nBaraye Cancel Kardan : /cancel or /start or /panel 🚫**')

        @Bot.on(events.CallbackQuery(data='AdminsList', func=CheckCreator)) 
        async def AdminsList(event:events.CallbackQuery.Event):
            Admins,Num = '',0
            if Data['Admins'] == []:
                await event.reply('** Admini Nist :) **')
            else:
                for i in Data['Admins']:
                    Num += 1
                    Admins += f"{Num}) {str(i)} 🫡 \n"
                await Bot.send_message(event.sender_id,Admins)

        @Bot.on(events.CallbackQuery(data='Data', func=CheckCreator))
        async def RefreshDataBot(event):
            global AllPost
            await RefreshDataFunc()
            AllPost = {}
            await Bot.send_message(event.sender_id, '** Restarted ☑️**')

        async def RefreshDataFunc():
            global Data
            Data = loads(open('Database/Config.json', 'r').read())

        @Bot.on(events.CallbackQuery(data='Close', func=AdAndCr))
        async def ClosePanel(event: events.CallbackQuery.Event):
            await event.edit('** Panel Closed ✔️**')

        @Bot.on(events.NewMessage(pattern='^/start Vid19KoSi', func=lambda e: e.is_private))
        async def Start(event: custom.message.Message):
            global Post, IDPost
            IDPost = int(event.raw_text.replace('/start Vid19KoSi', ''))
            Post = event.raw_text.replace('/start ', '')
            Status = await ForcedToJoin(event.sender_id)
            Database(UserID=event.sender_id,Data=Data).RefreshUser()
            await RefreshDataFunc()
            if Status:
                if Post in Data['Post']:
                    try:
                        Send1 = await Bot.send_message(event.sender_id,AllPost[f"{str(IDPost)}"])
                        await sleep(SleepForDelPost)
                        await Send1.delete()
                    except KeyError:
                        VideoForSave = await Bot.forward_messages(PeerUser(Creator[0]),int(IDPost),PeerChannel(Data['PostChannel']))
                        AllPost[f"{str(Post.replace('Vid19KoSi', ''))}"] = VideoForSave
                        await VideoForSave.delete()
                        Send2 = await Bot.send_message(event.sender_id,AllPost[f"{str(IDPost)}"])
                        await sleep(SleepForDelPost)
                        await Send2.delete()
                    except MessageIdInvalidError:
                        Database(Select='Remove', PostID=event.raw_text.replace('/start ', ''),Data=Data).RefreshPost()
                        del AllPost[f"{str(IDPost)}"]
                        await RefreshDataFunc()
                    except FloodWaitError:
                        await event.reply('لطفا چند دقیقه دیگه امتحان کنید | زیرا به دلیل ارسال زیاد ربات از طرف تلگرام محدود شده')

        @Bot.on(events.CallbackQuery(data='CheckJoin'))
        async def CheckJoin(event: events.CallbackQuery.Event):
            Status = await ForcedToJoin(event.sender_id)
            if Status:
                await event.answer(message='🌹 ممنون بابت عضو شدنت 🌹')
                await event.delete()
                try:
                    Send1 = await Bot.send_message(event.sender_id, AllPost[f"{str(IDPost)}"])
                    await sleep(SleepForDelPost)
                    await Send1.delete()
                except KeyError:
                    VideoForSave = await Bot.forward_messages(PeerUser(Creator[0]), int(IDPost),PeerChannel(Data['PostChannel']))
                    AllPost[f"{str(Post.replace('Vid19KoSi', ''))}"] = VideoForSave
                    await VideoForSave.delete()
                    Send2 = await Bot.send_message(event.sender_id, AllPost[f"{str(IDPost)}"])
                    await sleep(SleepForDelPost)
                    await Send2.delete()
                except MessageIdInvalidError:
                    Database(Select='Remove', PostID=event.raw_text.replace('/start ', ''), Data=Data).RefreshPost()
                    del AllPost[f"{str(IDPost)}"]
                    await RefreshDataFunc()
                except FloodWaitError:
                    await event.reply('لطفا چند دقیقه دیگه امتحان کنید | زیرا به دلیل ارسال زیاد ربات از طرف تلگرام محدود شده')

        @Bot.on(events.ChatAction(func=lambda e: e.is_group))
        async def LeftTheGroup(event: events.ChatAction.Event):
            await Bot.send_message(event.chat_id, '**ربات درون هیچ گروهی نمیتواند عضو باشد \n موفق باشید 🫡**')
            await Bot.delete_dialog(event.chat_id)

        @Bot.on(events.NewMessage(chats=Data['PostChannel'], func=lambda e: e.is_channel))
        async def UploadPost(event: custom.message.Message):
            LinkPost = (f"Vid19KoSi{event.message.id}")
            Database(Select='Add', PostID=LinkPost,Data=Data).RefreshPost()
            AllPost[f"{str(LinkPost.replace('Vid19KoSi',''))}"] = event.message
            try:
                for i in Creator:
                    await Bot.send_message(PeerUser(i), f'**🔴 Post Jadid Upload Shod , Link :🔷 t.me/{UserNameBot}?start={LinkPost} 🔷**')
                    sleep(0.2)
                for i in Data['Admins']:
                    await Bot.send_message(PeerUser(i), f'**🔴 Post Jadid Upload Shod , Link :🔷 t.me/{UserNameBot}?start={LinkPost} 🔷**')
                    sleep(0.2)
            except Exception as ex:
                print(str(ex))

    except Exception as ex:
        print(str(ex))
# ----------------------------------------------------- Run -------------------------------------------------------------
print('Bot is Online')
Bot.loop.create_task(main())
Bot.run_until_disconnected()
