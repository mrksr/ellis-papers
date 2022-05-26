import sys

import openreview
from tqdm import tqdm

if len(sys.argv) < 3:
    print("Usage: iclr_2022.py <username> <password>")
    sys.exit(1)

client = openreview.Client(
    baseurl="https://api.openreview.net",
    username=sys.argv[-2],
    password=sys.argv[-1],
)

iclr_submissions = openreview.tools.iterget_notes(
    client, invitation="ICLR.cc/2022/Conference/-/Blind_Submission"
)
iclr_submissions = {sub.forum: sub for sub in iclr_submissions}

iclr_decisions = openreview.tools.iterget_notes(
    client, invitation="ICLR.cc/2022/Conference/Paper.*/-/Decision"
)
iclr_decisions = {dec.forum: dec for dec in iclr_decisions}

accepted_iclr_submissions = {
    forum: sub
    for forum, sub in iclr_submissions.items()
    if "Accept" in iclr_decisions.get(forum, "").content["decision"]
}

authors_with_accepted_submissions = set(
    author_id
    for sub in accepted_iclr_submissions.values()
    for author_id in sub.content["authorids"]
)


def get_author_info(author):
    try:
        profile = client.get_profile(author).content
    except:
        return None

    names = profile["names"][0]
    return {
        "name": f"{names.get('first', '')} {names.get('last', '')}",
        "domains": [mail.split("@", 2)[-1] for mail in profile["emails"]],
    }


author_infos = {
    author: get_author_info(author)
    for author in tqdm(authors_with_accepted_submissions)
}
author_infos = {
    author: author_info
    for author, author_info in author_infos.items()
    if author_info is not None
}

for info in sorted(author_infos.values(), key=lambda info: info["name"]):
    print(info["name"], *info["domains"], sep=",")
