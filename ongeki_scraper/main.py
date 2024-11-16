import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import NamedTuple


ONGEKI_MOBILE="https://ongeki-net.com/ongeki-mobile/"
class ONGEKIError(Exception):
    pass
class ONGEKI():
    def __init__(self,sega_id:str=None,password:str=None,token:str=None,user_id:str=None,proxy:dict=None):
        self.sega_id=sega_id
        self.password=password
        self.token=token
        self.user_id=user_id
        if token and user_id:
            self.session=requests.Session()
            self.session.headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
            self.session.cookies.set("_t",token)
            self.session.cookies.set("userId",user_id)
        else:
            self.session=requests.Session()
            self.session.headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
            self.session.proxies=proxy
    
        if self.token:
            homo=self.session.get(ONGEKI_MOBILE+"home/playerDataDetail")
            if homo.status_code==302:
                raise ONGEKIError("セッションが期限切れです")
            
            user_settings=self.session.get(ONGEKI_MOBILE+"home/userOption")
            soup=BeautifulSoup(user_settings.content,"html.parser")
            try:
                course=soup.find("td").text
            except:
                raise ONGEKIError("セッションが期限切れです")

            if "プレミアム" in course:
                self.course="プレミアム"
            elif "スタンダード" in course:
                self.course="スタンダード"
            else:
                self.course="無料"

        else:
            login_form={
                "segaId": self.sega_id,
                "password": self.password,
                "save_cookie": "save_cookie"
            }
            self.session.get(ONGEKI_MOBILE)
            login_form["token"]=self.session.cookies["_t"]
            self.session.post(ONGEKI_MOBILE+"submit",data=login_form)
            aime_list=self.session.get(ONGEKI_MOBILE+"aimeList")
            if aime_list.status_code==302:
                raise ONGEKIError("ログイン情報が間違っています")

            soup=BeautifulSoup(aime_list.content,"html.parser")
            course=soup.find("td").text
            if "プレミアム" in course:
                self.course="プレミアム"
            elif "スタンダード" in course:
                self.course="スタンダード"
            else:
                self.course="無料"

            self.session.get(ONGEKI_MOBILE+"aimeList/submit/?idx=0")
            homo=self.session.get(ONGEKI_MOBILE+"home/playerDataDetail")
            try:
                self.token=self.session.cookies["_t"]
            except:
                ONGEKIError("現在メンテナンス中です")
            self.user_id=self.session.cookies["userId"]

        soup=BeautifulSoup(homo.content,"html.parser")
        self.name=soup.find(class_="name_block f_15").find("span").text
        self.plate=soup.find(class_="trophy_block trophy_1 f_11 f_b").find("span").text

        rating_field=soup.find(class_="rating_field t_l")
        self.rating=float(rating_field.find("span").text)

        self.raiting_max=float(soup.find(class_="rating_block f_14").find(class_="f_11").text.replace("（MAX ","").replace("）",""))
        self.leveling=int(soup.find(class_="lv_block white").find("span").text)
        reincarnation=soup.find(class_="reincarnation_block")
        if reincarnation:
            self.leveling_reincarnation=int(reincarnation.find("span").text)
        else:
            self.leveling_reincarnation=0

        self.battle_point=soup.find(class_="battle_rank_block").find("div").text
        self.icon=soup.find(class_="icon_block").find("img")["src"]
        self.character=soup.find(class_="home_character_block").find("img")["src"]
        mony_track=soup.find(class_="t_l f_13").find_all("td")
        money2=mony_track[2].text.replace(",","").replace("）","").split("（累計 ")
        self.money=money2[0]
        self.money_total=money2[1]
        self.tracks_total=mony_track[5].text

        self.activities=[]
        for activity in soup.find(class_="user_activity_table collapse t_l f_12").find_all("td"):
            if "しました！" in activity.text and "オンゲキ" not in activity.text:
                if "master.png" in activity.find("img")["src"]:
                    difficulty="Master"
                elif "expert.png" in activity.find("img")["src"]:
                    difficulty="Expert"
                elif "lunatic.png" in activity.find("img")["src"]:
                    difficulty="Lunatic"
                elif "advanced.png" in activity.find("img")["src"]:
                    difficulty="Advanced"
                elif "basic.png" in activity.find("img")["src"]:
                    difficulty="Basic"

                activity_text=activity.text.replace('\t', '').replace('\n', '').split("！")
                music_title=activity_text[1]
                music_activity=activity_text[0]+"！"
                self.activities.append(difficulty)
                self.activities.append(music_title)
                self.activities.append(music_activity)
            else:
                self.activities.append(activity.text.replace('\t', '').replace('\n', ''))

    
    def check_rating_music(self):
        rTM=self.session.get(ONGEKI_MOBILE+"home/ratingTargetMusic")
        soup=BeautifulSoup(rTM.content,"html.parser")
        rating_new=[]
        rating_best=[]
        rating_recent=[]
        rating_candidate=[]

        count=0
        for music in soup.find_all(action="https://ongeki-net.com/ongeki-mobile/record/musicDetail/"):
            title=music.find(class_="music_label p_5 break").text
            level=music.find(class_="score_level t_c").text
            score_str=music.find(class_="f_14 l_h_12").text
            score_int=int(score_str.replace(",",""))
            difficulty_image=music.find("img").find_next().find_next()["src"]
            if "master" in difficulty_image:
                difficulty="Master"
            elif "expert" in difficulty_image:
                difficulty="Expert"
            elif "lunatic" in difficulty_image:
                difficulty="Lunatic"
            elif "advanced" in difficulty_image:
                difficulty="Advanced"
            elif "basic" in difficulty_image:
                difficulty="Basic"

            idx=quote(music.find("input")["value"])
            
            if count<15:
                rating_new.append({"title":title,"level":level,"difficulty":difficulty,"technical_score":score_str,"technical_score_int":score_int,"idx":idx})
            elif count<45:
                rating_best.append({"title":title,"level":level,"difficulty":difficulty,"technical_score":score_str,"technical_score_int":score_int,"idx":idx})
            elif count<55:
                rating_recent.append({"title":title,"level":level,"difficulty":difficulty,"technical_score":score_str,"technical_score_int":score_int,"idx":idx})
            else:
                rating_candidate.append({"title":title,"level":level,"difficulty":difficulty,"technical_score":score_str,"technical_score_int":score_int,"idx":idx})
            count=count+1
            
        class RATING_LIST(NamedTuple):

            rating_new: list
            rating_best: list
            rating_recent: list
            rating_candidate: list

        return RATING_LIST(rating_new,rating_best,rating_recent,rating_candidate)
    
    def music_score_details(self,idx:str):
        details=self.session.get(ONGEKI_MOBILE+"record/musicDetail/?idx="+idx)
        soup=BeautifulSoup(details.content,"html.parser")
        music_details=soup.find(class_="m_10 t_l")
        music_img=music_details.find("img")["src"]
        music_title=music_details.find(class_="m_5 f_14 break").text
        music_genre=music_details.find(class_="t_r f_12 main_color").text.replace('\t', '').replace('\n', '')
        art_enemy=music_details.find(class_="m_5 f_13 break").text.replace('\t', '').split("\n")
        music_artist=art_enemy[1].strip()
        music_enemy=art_enemy[4].strip()

        master=soup.find(id="master")
        expert=soup.find(id="expert")
        lunatic=soup.find(id="lunatic")
        if master:
            level=master.find(class_="score_level t_c").text
            last_played=master.find("td").find_next().text
            plays=master.find("td",class_="t_r").text
            scores=master.find_all(class_="score_value master_score_value")
            over_damage=scores[0].text
            battle_score=scores[1].text
            technical_score=scores[2].text
            icons=master.find(class_="music_score_icon_area t_r f_0").find_all("img")
            icon_battle_rank=icons[0]["src"]
            icon_technical_rank=icons[1]["src"]
            icon_bell=icons[2]["src"]
            icon_combo=icons[3]["src"]
        else:
            level=None
            last_played=None
            plays=None
            scores=None
            over_damage=None
            battle_score=None
            technical_score=None
            icons=None
            icon_battle_rank=None
            icon_technical_rank=None
            icon_bell=None
            icon_combo=None
        
        if expert:
            level1=expert.find(class_="score_level t_c").text
            last_played1=expert.find("td").find_next().text
            plays1=expert.find("td",class_="t_r").text
            scores1=expert.find_all(class_="score_value expert_score_value")
            over_damage1=scores1[0].text
            battle_score1=scores1[1].text
            technical_score1=scores1[2].text
            icons1=expert.find(class_="music_score_icon_area t_r f_0").find_all("img")
            icon_battle_rank1=icons1[0]["src"]
            icon_technical_rank1=icons1[1]["src"]
            icon_bell1=icons1[2]["src"]
            icon_combo1=icons1[3]["src"]
        else:
            level1=None
            last_played1=None
            plays1=None
            scores1=None
            over_damage1=None
            battle_score1=None
            technical_score1=None
            icons1=None
            icon_battle_rank1=None
            icon_technical_rank1=None
            icon_bell1=None
            icon_combo1=None
        
        if lunatic:
            level2=lunatic.find(class_="score_level t_c").text
            last_played2=lunatic.find("td").find_next().text
            plays2=lunatic.find("td",class_="t_r").text
            scores2=lunatic.find_all(class_="score_value lunatic_score_value")
            over_damage2=scores2[0].text
            battle_score2=scores2[1].text
            technical_score2=scores2[2].text
            icons2=lunatic.find(class_="music_score_icon_area t_r f_0").find_all("img")
            icon_battle_rank2=icons2[0]["src"]
            icon_technical_rank2=icons2[1]["src"]
            icon_bell2=icons2[2]["src"]
            icon_combo2=icons2[3]["src"]
        else:
            level2=None
            last_played2=None
            plays2=None
            scores2=None
            over_damage2=None
            battle_score2=None
            technical_score2=None
            icons2=None
            icon_battle_rank2=None
            icon_technical_rank2=None
            icon_bell2=None
            icon_combo2=None
    
        class SCORE_DETAILS(NamedTuple):
            MASTER_level:str
            MASTER_last_played:str
            MASTER_play_count:str
            MASTER_over_damage:str
            MASTER_battle_score:str
            MASTER_technical_score:str
            MASTER_icon_battle_rank:str
            MASTER_icon_technical_rank:str
            MASTER_icon_bell:str
            MASTER_icon_combo:str

            EXPERT_level:str
            EXPERT_last_played:str
            EXPERT_play_count:str
            EXPERT_over_damage:str
            EXPERT_battle_score:str
            EXPERT_technical_score:str
            EXPERT_icon_battle_rank:str
            EXPERT_icon_technical_rank:str
            EXPERT_icon_bell:str
            EXPERT_icon_combo:str

            LUNATIC_level:str
            LUNATIC_last_played:str
            LUNATIC_play_count:str
            LUNATIC_over_damage:str
            LUNATIC_battle_score:str
            LUNATIC_technical_score:str
            LUNATIC_icon_battle_rank:str
            LUNATIC_icon_technical_rank:str
            LUNATIC_icon_bell:str
            LUNATIC_icon_combo:str
        
            music_img:str
            music_title:str
            music_genre:str
            music_artist:str
            music_enemy:str

        return SCORE_DETAILS(
        level,last_played,plays,over_damage,battle_score,technical_score,icon_battle_rank,icon_technical_rank,icon_bell,icon_combo,
        level1,last_played1,plays1,over_damage1,battle_score1,technical_score1,icon_battle_rank1,icon_technical_rank1,icon_bell1,icon_combo1,
        level2,last_played2,plays2,over_damage2,battle_score2,technical_score2,icon_battle_rank2,icon_technical_rank2,icon_bell2,icon_combo2,
        music_img,music_title,music_genre,music_artist,music_enemy)
    
    def playlog_score_details(self,idx:str):
        details=self.session.get(ONGEKI_MOBILE+"record/playlogDetail/?idx="+idx)
        soup=BeautifulSoup(details.content,"html.parser")
        music=soup.find(class_="m_10")
        if "master.png" in music.find("img")["src"]:
            music_difficulty="Master"
        elif "expert.png" in music.find("img")["src"]:
            music_difficulty="Expert"
        elif "lunatic.png" in music.find("img")["src"]:
            music_difficulty="Lunatic"
        elif "advanced.png" in music.find("img")["src"]:
            music_difficulty="Advanced"
        elif "basic.png" in music.find("img")["src"]:
            music_difficulty="Basic"

        played=soup.find(class_="f_r f_12 h_10").text
        music_img=soup.find(class_="m_5 f_l")["src"]
        music_title=soup.find(class_="m_5 l_h_10 break").text.replace('\t', '').replace('\n', '')
        music_scores=soup.find_all(class_="f_20")
        music_battle_score=music_scores[0].text
        music_over_damage=music_scores[1].text
        music_technical_score=music_scores[2].text
        clearfix=soup.find(class_="clearfix p_t_5 t_l f_0").find_all("img")
        if "base.png" in clearfix[0]:
            win=False
        else:
            win=True
        if "base.png" in clearfix[1]:
            full_bell=False
        else:
            full_bell=True
        if "base.png" in clearfix[2]:
            combo=False
        elif "fc.png" in clearfix[2]:
            combo="full combo"
        elif "ab.png" in clearfix[2]:
            combo="all break"
        
        score_detaile=soup.find_all(class_="score_detail_table")
        score_detaile2=score_detaile[1].find_all(class_="f_b")
        damage=score_detaile[0].find(class_="score_damage").find("td").text
        score_detaile=score_detaile[0].find_all(class_="f_b")
        max_combo=score_detaile[0].text
        critical_break=score_detaile[1].text
        ongeki_break=score_detaile[2].text
        hit=score_detaile[3].text
        miss=score_detaile[4].text
        bell=score_detaile[5].text

        tap=score_detaile2[0].text
        hold=score_detaile2[1].text
        flick=score_detaile2[2].text
        side_tap=score_detaile2[3].text
        side_hold=score_detaile2[4].text

        class SCORE_DETAILS(NamedTuple):
            music_played:str
            music_img:str
            music_title:str
            music_battle_score:str
            music_over_damage:str
            music_technical_score:str
            max_combo:str
            critical_break:str
            ongeki_break:str
            hit:str
            miss:str
            bell:str
            damage:str
            music_difficulty:str
            tap:str
            hold:str
            flick:str
            side_tap:str
            side_hold:str
            

        return SCORE_DETAILS(played,music_img,music_title,music_battle_score,music_over_damage,music_technical_score,
                           max_combo,critical_break,ongeki_break,hit,miss,bell,damage,music_difficulty,
                           tap,hold,flick,side_tap,side_hold)
        

    def get_all_music(self,difficulty:str="master"):
        if difficulty=="master":
            diff="3"
        elif difficulty=="expert":
            diff="2"
        elif difficulty=="advanced":
            diff="1"
        elif difficulty=="basic":
            diff="0"
        elif difficulty=="lunatic":
            diff="10"
        else:
            raise ONGEKIError("master / expert / advanced / basic / lunatic から選んでください")

        all_music=self.session.get(ONGEKI_MOBILE+"record/musicGenre/search/?genre=99&diff="+diff)
        soup=BeautifulSoup(all_music.content,"html.parser")
        musics=soup.find_all(class_=f"basic_btn {difficulty}_score_back m_10 p_5 t_l")
        music_dict={}
        for music in musics:
            music_title=music.find(class_="music_label p_5 break").text
            music_idx=quote(music.find("input")["value"])
            music_score=music.find(class_=f"score_table {difficulty}_score_table t_r clearfix")
            if music_score:
                music_scores=music_score.find_all(class_=f"score_value {difficulty}_score_value")
                music_battle_score=music_scores[0].text
                music_over_damage=music_scores[1].text
                music_technical_score=music_scores[2].text

                #if "back.png" in clearfix[1]:
                #    full_bell=False
                #else:
                #    full_bell=True
                #if "back.png" in clearfix[2]:
                #    combo=False
                #elif "fc.png" in clearfix[2]:
                #    combo="full combo"
                #elif "ab.png" in clearfix[2]:
                #    combo="all break"
            else:
                music_battle_score=None
                music_over_damage=None
                music_technical_score=None

            music_dict[music_title]={"idx":music_idx,"battle_score":music_battle_score,"over_damage":music_over_damage,"technical_score":music_technical_score}
        
        return music_dict

    def get_history(self):
        history=self.session.get(ONGEKI_MOBILE+"record/playlog")
        soup=BeautifulSoup(history.content,"html.parser")
        musics=soup.find_all(class_="m_10")
        music_list=[]
        for music in musics:
            if "master.png" in music.find("img")["src"]:
                music_difficulty="Master"
            elif "expert.png" in music.find("img")["src"]:
                music_difficulty="Expert"
            elif "lunatic.png" in music.find("img")["src"]:
                music_difficulty="Lunatic"
            elif "advanced.png" in music.find("img")["src"]:
                music_difficulty="Advanced"
            elif "basic.png" in music.find("img")["src"]:
                music_difficulty="Basic"

            played=music.find(class_="f_r f_12 h_10").text
            music_img=music.find(class_="m_5 f_l")["src"]
            music_title=music.find(class_="m_5 l_h_10 break").text.replace('\t', '').replace('\n', '')
            music_scores=music.find_all(class_="f_20")
            music_battle_score=music_scores[0].text
            music_over_damage=music_scores[1].text
            music_technical_score=music_scores[2].text
            clearfix=music.find(class_="clearfix p_t_5 t_l f_0").find_all("img")
            if "base.png" in clearfix[0]:
                win=False
            else:
                win=True
            if "base.png" in clearfix[1]:
                full_bell=False
            else:
                full_bell=True
            if "base.png" in clearfix[2]:
                combo=False
            elif "fc.png" in clearfix[2]:
                combo="full combo"
            elif "ab.png" in clearfix[2]:
                combo="all break"
                
            music_idx=quote(music.find("input")["value"])
            music_list.append({"title":music_title,"difficulty":music_difficulty,"technical_score":music_technical_score,"technical_score_int":int(music_technical_score.replace(",","")),"battle_score":music_battle_score,"over_damage":music_over_damage,"img":music_img,"played":played,"idx":music_idx})

        return music_list