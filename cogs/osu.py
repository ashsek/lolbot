import discord
from discord.ext import commands
from osuapi import OsuApi, AHConnector
import osuapi.enums
import utils.errors

class Osu:
    def __init__(self, bot):
        self.bot = bot
        if bot.config['osu']:
            self.api = OsuApi(bot.config['osu'], connector=AHConnector())
        else:
            self.api = None

    @classmethod
    def osu_mode_converter(self, mode=None):
        if mode is 0 or 'standard' or 'osu!standard' or 'osu!' or None:
            return osuapi.enums.OsuMode.osu
        elif mode is 1 or 'ctb' or 'catchthebeat' or 'osu!catch' or 'catch':
            return osuapi.enums.OsuMode.catch
        elif mode is 2 or 'taiko' or 'osu!taiko':
            return osuapi.enums.OsuMode.taiko
        elif mode is 3 or 'mania' or 'osu!mania':
            return osuapi.enums.OsuMode.mania
        else:
            return 'Unknown'


    @commands.group()
    async def osu(self, ctx):
        """Commands for osu!"""
        if ctx.invoked_subcommand is None:
            help_em = discord.Embed(title='Commands for osu!', colour=0x690E8)
            help_em.add_field(name='user', value='Gets info on osu! players. `^osu user *user*`')
            await ctx.send(embed=help_em)

    @osu.command()
    async def user(self, ctx, u: str, mode=None):
        """Returns information on a osu! player.
        If the player name you are searching has spaces, use quotation marks.
        e.g. ^osu user "player name with spaces"
        Special thanks to khazhyk for the library this command uses.

        By default this command defaults to osu!standard.
        All modes are supported.
        To use osu!standard, leave mode blank, or use 'standard', 'osu!standard', 'osu!' or 0.
        To use osu!catch, use 'catch', 'osu!catch', or 1.
        To use osu!taiko, use 'taiko', 'osu!taiko', or 2.
        To use osu!mania, use 'mania', 'osu!mania', or 3.
        Any other modes will return 'Unknown' error. (Service error)
        """
        if self.api:
            mode = self.osu_mode_converter(mode=mode)
            if mode == 'Unknown':
                raise utils.errors.ServiceError('Unknown mode')
            user = await self.api.get_user(u, mode=mode)
            try:
                user = user[0]
            except IndexError:
                return await ctx.send('User does not exist, maybe try one that does')
        else:
            raise utils.errors.ServiceError('osu! api key not configured')
        osu_embed = discord.Embed(title=f'osu! stats', colour=0x690E8)
        osu_embed.set_author(name=f'{u} ({user.country})',icon_url=f'https://osu.ppy.sh/images/flags/{user.country}.png')
        osu_embed.set_image(url=f'https://a.ppy.sh/{user.user_id}')
        osu_embed.add_field(name='User ID', value=user.user_id)
        osu_embed.add_field(name='Hits (300 score)', value=user.count300)
        osu_embed.add_field(name='Hits (100 score)', value=user.count100)
        osu_embed.add_field(name='Hits (50 score)', value=user.count50)
        osu_embed.add_field(name='Play count', value=user.playcount)
        osu_embed.add_field(name='Ranked score', value=user.ranked_score)
        osu_embed.add_field(name='Total score', value=user.total_score)
        osu_embed.add_field(name='Global rank', value=f'#{user.pp_rank}')
        osu_embed.add_field(name='Country rank', value=f'#{user.pp_country_rank}')
        osu_embed.add_field(name='Level', value=user.level)
        osu_embed.add_field(name='Total PP', value=user.pp_raw)
        osu_embed.add_field(name='Accuracy', value=f'{user.accuracy:.1f}%')
        osu_embed.add_field(name='Total SS plays', value=user.count_rank_ss)
        osu_embed.add_field(name='Total S plays', value=user.count_rank_s)
        osu_embed.add_field(name='Total A plays', value=user.count_rank_a)
        await ctx.send(embed=osu_embed)

def setup(bot):
    bot.add_cog(Osu(bot))
