from loaders.emailTextLoader import get_email_yesterday
from loaders.ytbChannelLoader import get_videos_yesterday
from utils.clean import remove_emojis, remove_stop
from utils.summarize import summarize_text

email_corpora = get_email_yesterday()
ytb_corpora = get_videos_yesterday()

corpora = email_corpora + ytb_corpora

corpora = remove_emojis(corpora)
corpora = remove_stop(corpora)

result = summarize_text(corpora)
