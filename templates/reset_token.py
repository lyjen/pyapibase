# -*- coding: utf-8 -*-
# pylint: disable=no-self-use, line-too-long, too-few-public-methods
"""Reset Token Template"""
from datetime import date
COPYRIGHT_YEAR = str(date.today().year)

class ResetToken():
    """Class for ResetToken"""

    # # INITIALIZE
    # def __init__(self):
    #     """The Constructor ResetToken class"""
    #     pass

    def reset_token_temp(self, reset_token):
        """Reset Token Temporarily"""
        email_temp = """
            <div style="background:#fcfcfc;font-family:arial,sans-serif;color:#474747;padding:2%">
                <table style="width:100%;max-width:600px;border:1px solid #dbdbdb;border-radius:5px;background:#fff;padding:0px;margin:0 auto 0px auto" border="0" cellspacing="0" cellpadding="0">
                    <tbody>
                        <tr>
                            <td style="padding:5px 30px 5px 30px;background:#7AC2AF;color:#fff;font-size:16px;text-align:left;font-weight:bold;border-radius:3px 3px 0 0;text-decoration:none">&nbsp;</td>
                        </tr>
                        <tr>
                            <td style="padding:15px 30px 10px;border-bottom:1px solid #dbdbdb"><a style="text-decoration:none" title="Lyjen" href="http://travel.lyjendary.com/" target="_blank" data-saferedirecturl="http://travel.lyjendary.com/"><img style="width:80%;max-width:100%;margin:0 auto;font-weight:bold;color:#222;font-size:38px;text-decoration:none" src="http://travel.lyjendary.com/assets/img/logo_lyjen.png" alt="Lyjen" class="CToWUd"></a></td>
                        </tr>
                        <tr>
                        <td style="padding:30px 30px 30px 30px">
                            <h1 style="font-family:arial,sans-serif;color:#222222;font-weight:bold;font-size:24px;margin:0;padding:0 0 20px 0;text-align:left">Authentication key for password reset</h1>
                            <p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5"><br>Use the authentication key to reset your password:</p>
                            <p style="background:#e1e1e1;padding:10px;border-radius:2px;font-weight:bold;color:#222222;font-size:18px">""" + reset_token + """</p>
                            <p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5">This temporary password will expire in 24 hours.</p>
                            <p style="font-family:arial,sans-serif;color:#474747;font-weight:normal;font-size:14px;margin:0;padding:0 0 0 0;text-align:left;line-height:1.5">If you didn’t make this request, simply ignore this message.</p>
                        </td>
                        </tr>
                    </tbody>
                </table>
                <table style="width:100%;max-width:600px;text-align:left;margin:20px auto 0 auto;font-family:arial,sans-serif;font-size:10px;color:#777777;line-height:1.3" border="0" cellspacing="0" cellpadding="0">
                    <tbody>
                        <tr>
                            <td style="width:100%;text-align:left;padding-bottom:10px">Copyright © <span class="il">Sample Template Lyjen</span> """+  COPYRIGHT_YEAR +"""</td>
                        </tr>
                    </tbody>
                </table>
                <div class="yj6qo">
                </div>
                <div class="adL">
                </div>
            </div>
        """
        return email_temp
