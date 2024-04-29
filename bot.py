"""
Основной файл, в котором прописана вся логика работы с дискордом
"""
import os
from contextlib import suppress
import discord
import requests
from discord.ext import commands
from discord.ext.commands import Context
import functions as fn
from config import path_to_ffmpeg
from TOKEN import token
from bcolors import Bcolors

intents = discord.Intents.all()
path = os.getcwd()
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready() -> None:
    """
    Функция, запускающаяся при запуске бота
    """
    print(Bcolors.OKGREEN + 'Бот запущен' + Bcolors.ENDC)


class Soundbar(discord.ui.View):
    """
    Главный класс, отвечающий за саму клавиатуру
    """

    def __init__(self):
        super().__init__(timeout=3600)


class ShowBar:
    """
    Вспомогательный класс для отображения всей звуковой панели сразу
    """

    def __init__(self, ctx: Context, cut_lst: list, message=None):
        """
        :param ctx:
        :param cut_lst: Список звуков для данной страницы
        :param message: Сообщение, которое нужно поменять. Если None, будет создано новое
        """
        self.ctx = ctx
        self.cut_lst = cut_lst
        self.message = message

    def show_bar(self) -> Soundbar:
        """
        :return: Объект клавиатуры
        """
        ctx = self.ctx
        lst = self.cut_lst
        view = Soundbar()

        length = 4
        row = 0
        for i in range(len(lst)):
            if i != 0 and i % length == 0:
                row += 1
            if self.message is None:
                cls = Sound(ctx, i, lst)
            else:
                cls = Sound(ctx, i, lst, message=self.message, view=view)
            view.add_item(fn.create_button(lst[i][1], func=cls.sound, style=discord.ButtonStyle.blurple, row=row))
        return view


class ShowPage:
    """
    Класс для отображения страницы звуковой панели
    """

    def __init__(self, ctx: Context, lst: list, lng: int, author, view: Soundbar, cut=(0, 16), edit=None):
        """
        :param ctx:
        :param lst: Список звуков
        :param lng: Ограничение на кол-во звуков в панели
        :param author: Кто вызвал звуковую панель
        :param view: Объект клавиатуры
        :param cut: Индексы, показывающие, какой срез списка нужен
        :param edit: Сообщение, которое нужно поменять. Если None, будет создано новое
        """
        self.ctx = ctx
        self.cut = cut
        self.lst = lst
        self.length = lng
        self.view = view
        self.edit = edit
        self.message = None
        self.show = None
        self.author = author

    async def add_sound(self) -> None:
        view = self.view
        ctx = self.ctx
        cut = self.cut
        lst = self.lst
        original_lst = lst.copy()
        lst = lst[cut[0]:cut[1]]
        length = 4
        row = 0
        for i in range(len(lst)):
            if i != 0 and i % length == 0:
                row += 1
            cls = Sound(ctx, i, lst)
            view.add_item(fn.create_button(lst[i][1], func=cls.sound, style=discord.ButtonStyle.blurple, row=row))

        async def back(interaction: discord.Interaction) -> None:
            """
            Функция для перелистывания страницы назад
            :param interaction:
            :return:
            """
            view.clear_items()
            embed = discord.Embed(description=f'{interaction.user.mention}, выберете звук:', color=0xFF8C00)
            # noinspection PyUnresolvedReferences
            await interaction.response.edit_message(embed=embed)
            await ShowPage(ctx, original_lst, self.length, interaction.user, view, cut=(cut[0] - 16, cut[1] - 16),
                           edit=self.message).add_sound()

        async def stop(interaction: discord.Interaction) -> None:
            """
            Функция для остановки воспроизведения звука
            :param interaction:
            :return:
            """
            flag = True if type(self.message) is list else False
            server = interaction.guild
            voice = discord.utils.get(bot.voice_clients, guild=server)
            with suppress(AttributeError):
                voice.pause()
            embed = discord.Embed(description=f'{interaction.user.mention}, выберете звук:', color=0xFF8C00)
            if not flag:
                # noinspection PyUnresolvedReferences
                await interaction.response.edit_message(embed=embed)
            else:
                await self.message[0].edit(embed=embed)
                # noinspection PyUnresolvedReferences
                await interaction.response.edit_message(view=self.show)

        async def quit_(interaction: discord.Interaction) -> None:
            """
            Функция для отключения бота от голосового канала
            :param interaction:
            :return:
            """
            flag = True if type(self.message) is list else False
            server = interaction.guild
            voice = discord.utils.get(bot.voice_clients, guild=server)
            with suppress(AttributeError):
                voice.pause()
            try:
                await voice.disconnect(force=True)
            except AttributeError:
                embed = discord.Embed(description=f'{interaction.user.mention}, я не нахожусь в голосовом канале',
                                      color=0xFF0000)
                if not flag:
                    # noinspection PyUnresolvedReferences
                    await interaction.response.edit_message(embed=embed)
                else:
                    await self.message[0].edit(embed=embed)
                    # noinspection PyUnresolvedReferences
                    await interaction.response.edit_message(view=self.show)
                return
            embed = discord.Embed(description=f'{interaction.user.mention}, Пока 👋', color=0xFF8C00)
            if not flag:
                # noinspection PyUnresolvedReferences
                await interaction.response.edit_message(embed=embed)
            else:
                await self.message[0].edit(embed=embed)
                # noinspection PyUnresolvedReferences
                await interaction.response.edit_message(view=self.show)

        async def forward(interaction: discord.Interaction) -> None:
            """
            Функция для перелистывания страницы вперёд.
            :param interaction:
            :return:
            """
            view.clear_items()
            embed = discord.Embed(description=f'{interaction.user.mention}, выберете звук:', color=0xFF8C00)
            # noinspection PyUnresolvedReferences
            await interaction.response.edit_message(embed=embed)
            await ShowPage(ctx, original_lst, self.length, interaction.user, view, cut=(cut[0] + 16, cut[1] + 16),
                           edit=self.message).add_sound()

        async def show_all(interaction: discord.Interaction) -> None:
            """
            Функция для отображения всей звуковой панели
            :param interaction:
            :return:
            """
            # noinspection PyUnresolvedReferences
            await interaction.response.edit_message(view=self.view)
            cut = (0, 16)
            lst = original_lst[cut[0]:cut[1]]
            message = None
            if lst[-1] != original_lst[-1]:
                view = ShowBar(ctx, lst).show_bar()
                embed = discord.Embed(description=f'{interaction.user.mention}, выберете звук:', color=0xFF8C00)
                message = await ctx.send(embed=embed, view=view)
                cut = (cut[0] + 16, cut[1] + 16)
                lst = original_lst[cut[0]:cut[1]]
            while lst[-1] != original_lst[-1]:
                view = ShowBar(ctx, lst, message=message).show_bar()
                cut = (cut[0] + 16, cut[1] + 16)
                lst = original_lst[cut[0]:cut[1]]
                await ctx.send(view=view)

            self.message = [message]
            view = ShowBar(ctx, lst, message=message).show_bar()
            self.show = view
            view.add_item(fn.create_button(name='Stop', func=stop, style=discord.ButtonStyle.red, row=row + 1))
            view.add_item(fn.create_button(name='Quit', func=quit_, style=discord.ButtonStyle.red, row=row + 1))
            await ctx.send(view=view)

        if cut[1] > 16:
            view.add_item(fn.create_button('⬅️', back, discord.ButtonStyle.green, row=row + 1))

        view.add_item(fn.create_button(name='Stop', func=stop, style=discord.ButtonStyle.red, row=row + 1))

        if len(original_lst) > 16:
            view.add_item(fn.create_button(name='Show all', func=show_all, style=discord.ButtonStyle.green,
                                           row=row + 1))

        view.add_item(fn.create_button(name='Quit', func=quit_, style=discord.ButtonStyle.red, row=row + 1))

        if cut[1] < len(original_lst) - 1:
            view.add_item(fn.create_button(name='➡️', func=forward, style=discord.ButtonStyle.green, row=row + 1))

        author = self.author
        if self.edit is None:
            embed = discord.Embed(description=f'{author.mention}, выберете звук:', color=0xFF8C00)
            self.message = await ctx.send(embed=embed, view=view)
        else:
            embed = discord.Embed(description=f'{author.mention}, выберете звук:', color=0xFF8C00)
            # noinspection PyUnresolvedReferences
            await self.edit.edit(embed=embed, view=view)
            self.message = self.edit


class Sound:
    """
    Класс, отвечающий за кнопку воспроизведения звука
    """

    def __init__(self, ctx: Context, k, lst: list, message=None, view=None):
        """
        :param ctx:
        :param k: Индекс звука в списке
        :param lst: Список звуков
        :param message: Сообщение, которое нужно поменять
        :param view: Объект клавиатуры
        """
        self.k = k
        self.lst = lst
        self.ctx = ctx
        self.message = message
        self.view = view

    async def sound(self, interaction: discord.Interaction) -> None:
        server = interaction.guild
        lst = self.lst
        k = self.k
        author = interaction.user
        try:
            name_channel = author.voice.channel.name
        except AttributeError:
            embed = discord.Embed(
                description=f'{author.mention}, вы сейчас не находитесь ни в одном голосовом канале',
                color=0xFF0000)
            if self.message is not None:
                await self.message.edit(embed=embed)
                # noinspection PyUnresolvedReferences
                await interaction.response.edit_message(view=self.view)
            else:
                # noinspection PyUnresolvedReferences
                await interaction.response.edit_message(embed=embed)
            return
        voice_channel = discord.utils.get(server.voice_channels, name=name_channel)
        voice = discord.utils.get(bot.voice_clients, guild=server)
        with suppress(AttributeError):
            voice.pause()
        params = lst[k]
        source = params[0]
        if voice is None:
            await voice_channel.connect()
            voice = discord.utils.get(bot.voice_clients, guild=server)
        elif voice_channel.name != str(self.ctx.voice_client.channel):
            await self.ctx.voice_client.disconnect(force=True)
            await voice_channel.connect()
            voice = discord.utils.get(bot.voice_clients, guild=server)
        if not (source is None):
            try:
                voice.play(discord.FFmpegPCMAudio(executable=path_to_ffmpeg, source=source))
            except discord.errors.ClientException:
                embed = discord.Embed(description=f'{author.mention}, ошибка при воспроизведении звука', color=0xFF0000)
                if self.message is not None:
                    await self.message.edit(embed=embed)
                    # noinspection PyUnresolvedReferences
                    await interaction.response.edit_message(view=self.view)
                else:
                    # noinspection PyUnresolvedReferences
                    await interaction.response.edit_message(embed=embed)
                return
        embed = discord.Embed(description=f'{author.mention}, сейчас играет "{lst[k][1]}"', color=0xFF8C00)
        if self.message is not None:
            await self.message.edit(embed=embed)
            # noinspection PyUnresolvedReferences
            await interaction.response.edit_message(view=self.view)
        else:
            # noinspection PyUnresolvedReferences
            await interaction.response.edit_message(embed=embed)


@bot.command()
@commands.guild_only()
async def soundbar(ctx: Context) -> None:
    """
    Команда для вызова звуковой панели
    :param ctx:
    :return:
    """
    result = fn.fetch_data(1, 2000, ctx.guild.id)
    lst = []
    for row in result:
        lst.append(row[1:])
    view = Soundbar()
    await ShowPage(ctx, lst, 2000, ctx.author, view).add_sound()


@bot.command()
@commands.guild_only()
async def load(ctx: Context, url: str, *name) -> None:
    """
    Команда для загрузки звука. Требуется указывать ссылку-установщик и желаемое имя. Если ссылки нет,
    ожидается прикрепленный файл.
    :param ctx:
    :param url: Ссылка-установщик (в случае отсутствия ожидается прикрепленный файл)
    :param name: Желаемое название звука
    :return:
    """
    extensions = ['.aac', '.ac3', '.aif', '.aiff', '.amr', '.aob', '.ape', '.asf', '.aud', '.awb', '.bin', '.bwg',
                  '.cdr', '.flac', '.gpx', '.ics', '.iff', '.m', '.m3u', '.m3u8', '.m4a', '.m4b', '.m4r', '.mid',
                  '.midi', '.mod', '.mp3', '.mpa', '.mpp', '.msc', '.msv', '.mts', '.nkc', '.ogg', '.ps', '.ra',
                  '.ram', '.sdf', '.sib', '.sln', '.spl', '.srt', '.temp', '.vb', '.wav', '.wave', '.wm', '.wma',
                  '.wpd', '.xsb', '.xwb']
    try:
        requests.get(url)
        author = ctx.author
        if not name:
            embed = discord.Embed(
                description=f'{author.mention}, не указано название звука',
                color=0xFF0000)
            await ctx.send(embed=embed)
            return
        check = ''.join(name)
        flag = True
        for i in check:
            if i.isalnum():
                flag = False
                break
        if flag:
            embed = discord.Embed(
                description=f'{author.mention}, не указано название звука',
                color=0xFF0000)
            await ctx.send(embed=embed)
            return
        name = ' '.join(name)
        author = ctx.author
        directory = path + '/guild' + str(ctx.guild.id)
        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = path + '/guild' + str(ctx.guild.id)
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_name = os.path.basename(url)
            file_path = os.path.join(directory, file_name)
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
        else:
            embed = discord.Embed(
                description=f'{author.mention}, я не могу установить {url}, '
                            f'потому что я не могу получить доступ к сайту',
                color=0xFF0000)
            await ctx.send(embed=embed)
            return
        fn.first_join(str(file_path), str(name), int(ctx.guild.id))
        embed = discord.Embed(description=f'{author.mention}, звук был успешно добавлен.', color=0xFF8C00)
        await ctx.send(embed=embed)

    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidURL):
        name = [url] + list(name)
        if len(ctx.message.attachments) == 0:
            embed = discord.Embed(title='Файл не найден', color=0xFF0000)
            await ctx.send(embed=embed)
            return
        elif len(ctx.message.attachments) > 1:
            embed = discord.Embed(title=f'Ошибка: требуется 1 файл, найдено {len(ctx.message.attachments)}',
                                  color=0xFF0000)
            await ctx.send(embed=embed)
            return
        else:
            url = ctx.message.attachments[0]
        author = ctx.author
        name = ' '.join(name)

        directory = path + '/guild' + str(ctx.guild.id)

        if not os.path.exists(directory):
            os.makedirs(directory)

        file_name = fn.found_mp3(str(url))
        flag = True
        for ext in extensions:
            if file_name.endswith(ext):
                flag = False
                break
        if flag:
            embed = discord.Embed(description=f'{author.mention}, файл {file_name} имеет неподдерживаемое '
                                              f'расширение.', color=0xFF0000)
            await ctx.send(embed=embed)
            return
        file_path = os.path.join(directory, file_name)
        # noinspection PyTypeChecker
        await url.save(file_path)
        fn.first_join(str(file_path), str(name), int(ctx.guild.id))
        embed = discord.Embed(description=f'{author.mention}, звук был успешно добавлен.', color=0xFF8C00)
        await ctx.send(embed=embed)


@bot.command()
@commands.guild_only()
async def delete(ctx: Context, *name) -> None:
    """
    Удаление звука
    :param ctx:
    :param name: Название звука
    :return:
    """
    name = ' '.join(name)
    author = ctx.author
    sound_path = fn.path_to_delete(name, int(ctx.guild.id))
    if sound_path is None:
        embed = discord.Embed(description=f'{author.mention}, звук с таким именем не найден', color=0xFF0000)
        await ctx.send(embed=embed)
        return
    try:
        fn.delete_sound(sound_path, int(ctx.guild.id))
    except TypeError:
        embed = discord.Embed(description=f'{author.mention}, Вы не указали название звука', color=0xFF0000)
        await ctx.send(embed=embed)
        return
    os.remove(sound_path)
    embed = discord.Embed(description=f'{author.mention}, звук "{name}" был удален.', color=0xFF8C00)
    await ctx.send(embed=embed)


# noinspection SpellCheckingInspection
bot.run(token)
