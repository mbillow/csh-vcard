# CSH LDAP to vCard
# By: Marc Billow
# mbillow@csh.rit.edu

from flask import Flask, Response
import CSHLDAP
import hashlib
import urllib2
import argparse


def listify(item):
    return item if isinstance(item, list) else [item]


def format_base64(raw_base):
    base64 = raw_base.replace("\n", "")
    current_char = 49
    last_char = 124
    formatted_base = base64[:49] + "\n "
    while True:
        formatted_base += base64[current_char:last_char] + "\n "
        if current_char <= len(base64)-76:
            current_char += 75
            last_char += 75
        else:
            current_char += 75
            last_char = len(base64)
            formatted_base += base64[current_char:last_char]
            break

    return formatted_base


def gravatar_base64(email):
    email_hash = hashlib.md5(email)
    try:
        image_url = "http://www.gravatar.com/avatar/" + email_hash.hexdigest() + ".jpg"
        gravatar_request = urllib2.urlopen(image_url)
        base64 = gravatar_request.read().encode("base64")
        # Don't assign contact image 
        static_image = urllib2.urlopen("http://www.gravatar.com/avatar/static.jpg")
        static_base64 = static_image.read().encode("base64")
        if base64 != static_base64:
            return format_base64(base64)
        else:
            return ""
    except:
        return ""


def jpeg_to_base64(jpeg):
    base64 = jpeg.encode("base64")
    return format_base64(base64)


def get_fullname(user):
    fn = listify(user.givenName)[0]
    ln = user.sn
    return str(fn + " " + ln)


def format_card(user):
    item_counter = 1
    vcard = "BEGIN:VCARD\nVERSION:3.0\n"
    vcard += "N:" + user.sn + ";" + listify(user.givenName)[0] + ";;;\n" \
        + "FN:" + get_fullname(user) + "\n"
    if user.nickname is not None:
        vcard += "NICKNAME:" + user.nickname + "\n"
    if user.mail:
        emails = listify(user.mail)
        for email in emails:
            vcard += "item" + str(item_counter) + ".EMAIL;TYPE=INTERNET;type=pref:" + email \
                + "\nitem" + str(item_counter) + ".X-ABLabel:work\n"
            item_counter += 1
    else:
        print user.givenName + " does not have any email addresses."

    if user.mobile:
        vcard += "TEL;type=MOBILE;type=CELL;type=VOICE;type=pref:" + str(user.mobile) + "\n"
    else:
        print user.givenName + " does not have any phone numbers."
    if user.homepageURL:
        urls = listify(user.homepageURL)
        for site in urls:
            vcard += "item" + str(item_counter) + ".URL;type=pref:" + site \
                + "\nitem" + str(item_counter) + ".X-ABLabel:_$!<HomePage>!$_\n"
            item_counter += 1
    else:
        print user.givenName + " does not have any web sites."

    if user.blogURL:
        urls = listify(user.blogURL)
        for site in urls:
            vcard += "item" + str(item_counter) + ".URL;type=pref:" + site \
                + "\nitem" + str(item_counter) + ".X-ABLabel:blog\n"
            item_counter += 1
    else:
        print user.givenName + " does not have any blogs."

    if user.github:
        vcard += "item" + str(item_counter) + ".URL;type=pref:https://www.github.com/" + user.github \
            + "\nitem" + str(item_counter) + ".X-ABLabel:github\n"
        item_counter += 1
    if user.twitter:
        vcard += "item" + str(item_counter) + ".URL;type=pref:https://www.twitter.com/" + user.twitter \
            + "\nitem" + str(item_counter) + ".X-ABLabel:twitter\n"
    if user.jpegPhoto == "" or user.jpegPhoto is None:
        vcard += "PHOTO;TYPE=JPEG;ENCODING=b:" + gravatar_base64(listify(user.mail)[0]) + "\nEND:VCARD"
    else:
        vcard += "PHOTO;TYPE=JPEG;ENCODING=b:" + jpeg_to_base64(user.jpegPhoto) + "\nEND:VCARD"
    return vcard


def get_user_info(get_user):
    ldap = CSHLDAP.CSHLDAP("", "")
    user = ldap.member(get_user, objects=True)
    return user


def write_card(name, card_content):
    card = open((name + ".vcf"), "wb")
    card.write(card_content)

app = Flask(__name__)


@app.route("/<username>.vcf", methods=["GET"])
def vcard(username):
    vcard = format_card(get_user_info(username))
    if not vcard:
        return Response("Whoops. Can't generate vCard for that user!", status=500)
    return Response(vcard, headers={"Content-Type": "text/vcard"})


if __name__ == "__main__":
    #if len(sys.argv) < 2:
    #    print("Usage: CSH-LDAP.py [username, ...]")
    #for uid in sys.argv[1:]:
    #    user_object = get_user_info(uid)
    #    try:
    #        card_info = format_card(user_object)
    #        write_card(card_info[0], card_info[1])
    #    except AttributeError:
    #        print("User not found!")

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test",
                        help="Runs the server in test mode and updates the"
                             " testUsers database.",
                        action="store_true")

    args = parser.parse_args()

    app.run(host='0.0.0.0', port=42010, debug=args.test)




