import requests
from bs4 import BeautifulSoup
from typing import NamedTuple


CHUNITHM_MOBILE="https://new.chunithm-net.com/chuni-mobile/html/mobile/"
class CHUNITHMError(Exception):
    pass
class CHUNITHM():
    def __init__(self,sega_id:str=None,password:str=None,token:str=None,php_sess_id:str=None,proxy:dict=None):
        self.sega_id=sega_id
        self.password=password
        self.token=token
        self.php_sess_id=php_sess_id
        if token and php_sess_id:
            self.session=requests.Session()
            self.session.headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
            self.session.cookies.set("_t",token)
            self.session.cookies.set("PHPSESSID",php_sess_id)
        else:
            self.session=requests.Session()
            self.session.headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"}
            self.session.proxies=proxy

        if self.token:
            homo=self.session.get(CHUNITHM_MOBILE+"home/playerData")
            if homo.status_code==302:
                raise CHUNITHMError("セッションが期限切れです")
            
            aime_list=self.session.get(CHUNITHM_MOBILE+"aimeList")
            if aime_list.status_code==302:
                raise CHUNITHMError("セッションが期限切れです")

            soup=BeautifulSoup(aime_list.content,"html.parser")
            course=soup.find(class_="mr_10").find_next().text

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
            self.session.get(CHUNITHM_MOBILE)
            try:
                login_form["token"]=self.session.cookies["_t"]
            except:
                raise CHUNITHMError("現在メンテナンス中です")
            self.session.post(CHUNITHM_MOBILE+"submit",data=login_form)
            aime_list=self.session.get(CHUNITHM_MOBILE+"aimeList")
            if aime_list.status_code==302:
                raise CHUNITHMError("ログイン情報が間違っています")
            soup=BeautifulSoup(aime_list.content,"html.parser")
            course=soup.find(class_="mr_10").find_next().text
            if "プレミアム" in course:
                self.course="プレミアム"
            elif "スタンダード" in course:
                self.course="スタンダード"
            else:
                self.course="無料"

            self.token=self.session.cookies["_t"]
            self.session.post(CHUNITHM_MOBILE+"aimeList/submit",data={"idx":"0","token":self.token})
            homo=self.session.get(CHUNITHM_MOBILE+"home/playerData")
            self.php_sess_id=self.session.cookies["PHPSESSID"]
        
        soup=BeautifulSoup(homo.content,"html.parser")
        self.name=soup.find(class_="player_name_in").text
        self.plate=soup.find(class_="player_honor_text_view").find("span").text
        rating_img=soup.find(class_="player_rating_num_block").find_all("img")
        rating_nums=""
        for rating_num in rating_img:
            rating_num=rating_num["src"][-5]
            if rating_num=="a":
                rating_num="."
            rating_nums=rating_nums+rating_num
        
        self.rating=float(rating_nums)
        #self.raiting_max=float(soup.find(class_="player_rating_max").text) 突然消えた
        self.leveling=int(soup.find(class_="player_lv").text)
        reincarnation=soup.find(class_="player_reborn")
        if reincarnation:
            self.leveling_reincarnation=int(reincarnation.text)
        else:
            self.leveling_reincarnation=0
        
        overpower=soup.find(class_="player_overpower_text")
        if overpower:
            self.overpower=overpower.text
        else:
            self.overpower=0
        
        self.last_play=soup.find(class_="player_lastplaydate_text").text
        self.battle_rank=soup.find(class_="player_battlerank").find("img")["src"]#.split("battlerank_")[1].replace(".png","")
        self.icon=soup.find(class_="player_chara").find("img")["src"]
        #self.character=soup.find(class_="player_chara").find("img")["src"]
        self.money=soup.find(class_="user_data_point").find(class_="user_data_text").text
        self.money_total=soup.find(class_="user_data_total_point").find(class_="user_data_text").text
        self.tracks_total=soup.find(class_="user_data_play_count").find(class_="user_data_text").text

    
    def check_rating_music(self,type="Best"):
        rTM=self.session.get(CHUNITHM_MOBILE+f"home/playerData/ratingDetail{type}")
        soup=BeautifulSoup(rTM.content,"html.parser")
        rating=[]
        for music in soup.find_all(action="https://new.chunithm-net.com/chuni-mobile/html/mobile/record/musicGenre/sendMusicDetail/"):
            title=music.find(class_="music_title").text
            score_str=music.find(class_="text_b").text
            score_int=int(score_str.replace(",",""))
            difficulty_image=music.find("div")["class"]
            if "master" in difficulty_image[2]:
                difficulty="Master"
            elif "expert" in difficulty_image[2]:
                difficulty="Expert"
            elif "ultima" in difficulty_image[2]:
                difficulty="Ultima"
            elif "advanced" in difficulty_image[2]:
                difficulty="Advanced"
            elif "basic" in difficulty_image[2]:
                difficulty="Basic"

            hiddens=music.find_all("input")
            
            rating.append({"title":title,"difficulty":difficulty,"score":score_str,"score_int":score_int,"diff":hiddens[0]["value"],"genre":hiddens[1]["value"],"idx":hiddens[2]["value"],"token":hiddens[3]["value"]})

        return rating
    
    def music_score_details(self,idx:str,token:str,diff:str=None,genre:str=None):
        hidden_form={
            #"diff": diff,
            #"genre": genre,
            "idx": idx,
            "token": token
        }
        if diff:
            hidden_form["diff"]=diff

        if genre:
            hidden_form["genre"]=genre

        self.session.post(CHUNITHM_MOBILE+"record/musicGenre/sendMusicDetail",data=hidden_form)
        details=self.session.get(CHUNITHM_MOBILE+"record/musicDetail")
        soup=BeautifulSoup(details.content,"html.parser")
        music_details=soup.find(class_="frame02 w420")
        music_img=music_details.find(class_="play_jacket_img").find("img")["src"]
        music_title=music_details.find(class_="play_musicdata_title").text
        music_artist=music_details.find(class_="play_musicdata_score play_musicdata_artist").text

        master=soup.find(class_="w420 music_box bg_master")
        expert=soup.find(class_="w420 music_box bg_expert")
        ultima=soup.find(class_="w420 music_box bg_ultima")
        if master:
            play_scores=master.find_all(class_="musicdata_score_num")
            plays=play_scores[1].find(class_="text_b").text
            score=play_scores[0].find(class_="text_b").text
            icons=master.find(class_="play_musicdata_icon clearfix mb_5").find_all("img")
            if "icon_clear.png" in icons[0]["src"]:
                icon_clear=icons[0]["src"]
                icon_technical_rank=icons[1]["src"]
                if len(icons)==1:
                    icon_combo=None
                else:
                    icon_combo=icons[1]["src"]
                
            else:
                icon_clear=None
                icon_technical_rank=icons[0]["src"]
                if len(icons)==1:
                    icon_combo=None
                else:
                    icon_combo=icons[1]["src"] 
        else:
            plays=None
            score=None
            icon_technical_rank=None
            icon_clear=None
            icon_combo=None
        
        if expert:
            play_scores=expert.find_all(class_="musicdata_score_num")
            plays1=play_scores[1].find(class_="text_b").text
            score1=play_scores[0].find(class_="text_b").text
            icons=expert.find(class_="play_musicdata_icon clearfix mb_5").find_all("img")
            if "icon_clear.png" in icons[0]["src"]:
                icon_clear1=icons[0]["src"]
                icon_technical_rank1=icons[1]["src"]
                if len(icons)==1:
                    icon_combo1=None
                else:
                    icon_combo1=icons[1]["src"]
                
            else:
                icon_clear1=None
                icon_technical_rank1=icons[0]["src"]
                if len(icons)==1:
                    icon_combo1=None
                else:
                    icon_combo1=icons[1]["src"] 
        else:
            plays1=None
            score1=None
            icon_technical_rank1=None
            icon_clear1=None
            icon_combo1=None
        
        if ultima:
            play_scores=ultima.find_all(class_="musicdata_score_num")
            plays2=play_scores[1].find(class_="text_b").text
            score2=play_scores[0].find(class_="text_b").text
            icons=ultima.find(class_="play_musicdata_icon clearfix mb_5").find_all("img")
            if "icon_clear.png" in icons[0]["src"]:
                icon_clear2=icons[0]["src"]
                icon_technical_rank2=icons[1]["src"]
                if len(icons)==1:
                    icon_combo2=None
                else:
                    icon_combo2=icons[1]["src"]
                
            else:
                icon_clear2=None
                icon_technical_rank2=icons[0]["src"]
                if len(icons)==1:
                    icon_combo2=None
                else:
                    icon_combo2=icons[1]["src"] 
        else:
            plays2=None
            score2=None
            icon_technical_rank2=None
            icon_clear2=None
            icon_combo2=None
    
        class SCORE_DETAILS(NamedTuple):
            MASTER_play_count:str
            MASTER_score:str
            MASTER_icon_rank:str
            MASTER_icon_combo:str
            MASTER_icon_clear:str

            EXPERT_play_count:str
            EXPERT_score:str
            EXPERT_icon_rank:str
            EXPERT_icon_combo:str
            EXPERT_icon_clear:str

            ULTIMA_play_count:str
            ULTIMA_score:str
            ULTIMA_icon_rank:str
            ULTIMA_icon_combo:str
            ULTIMA_icon_clear:str
        
            music_img:str
            music_title:str
            music_artist:str

        return SCORE_DETAILS(
        plays,score,icon_technical_rank,icon_combo,icon_clear,
        plays1,score1,icon_technical_rank1,icon_combo1,icon_clear1,
        plays2,score2,icon_technical_rank2,icon_combo2,icon_clear2,
        music_img,music_title,music_artist)
    
    def playlog_score_details(self,idx:str,token:str):
        hidden_form={
            "idx": idx,
            "token": token
        }

        self.session.post(CHUNITHM_MOBILE+"record/playlog/sendPlaylogDetail",data=hidden_form)
        details=self.session.get(CHUNITHM_MOBILE+"record/playlogDetail")
        soup=BeautifulSoup(details.content,"html.parser")
        music=soup.find(class_="box01 w420")
        diff=music.find(class_="play_track_result").find("img")["src"]
        if "master.png" in diff:
            music_difficulty="Master"
        elif "expert.png" in diff:
            music_difficulty="Expert"
        elif "ultima.png" in diff:
            music_difficulty="Ultima"
        elif "advanced.png" in diff:
            music_difficulty="Advanced"
        elif "basic.png" in diff:
            music_difficulty="Basic"

        played=soup.find(class_="box_inner01").text
        music_img=soup.find(class_="play_jacket_img").find("img")["src"]
        music_title=soup.find(class_="play_musicdata_title").text
        music_score=soup.find(class_="play_musicdata_score_text").text
        icons=soup.find(class_="play_musicdata_icon clearfix").find_all("img")
        character=soup.find(class_="play_data_chara_name").text
        skill=soup.find(class_="play_data_skill_name").text
        if "icon_clear.png" in icons[0]["src"]:
            icon_clear=icons[0]["src"]
            icon_technical_rank=icons[1]["src"]
            if len(icons)==1:
                icon_combo=None
            else:
                icon_combo=icons[1]["src"]
            
        else:
            icon_clear=None
            icon_technical_rank=icons[0]["src"]
            if len(icons)==1:
                icon_combo=None
            else:
                icon_combo=icons[1]["src"] 
        
        score_detaile=soup.find(class_="play_data_detail_block")
        max_combo=score_detaile.find(class_="play_data_detail_maxcombo_block font_large").text
        critical_break=score_detaile.find(class_="text_critical play_data_detail_judge_text").text
        chunithm_break=score_detaile.find(class_="text_justice play_data_detail_judge_text").text
        hit=score_detaile.find(class_="text_attack play_data_detail_judge_text").text
        miss=score_detaile.find(class_="text_miss play_data_detail_judge_text").text

        tap=score_detaile.find(class_="font_90 text_tap_red play_data_detail_notes_text").text
        hold=score_detaile.find(class_="font_90 text_hold_yellow play_data_detail_notes_text").text
        slide=score_detaile.find(class_="font_90 text_slide_blue play_data_detail_notes_text").text
        air=score_detaile.find(class_="font_90 text_air_green play_data_detail_notes_text").text
        flick=score_detaile.find(class_="font_90 text_flick_skyblue play_data_detail_notes_text").text
        

        class SCORE_DETAILS(NamedTuple):
            music_played:str
            music_img:str
            music_title:str
            music_score:str
            music_difficulty:str

            character:str
            skill:str
            max_combo:str
            justice_critical:str
            justice:str
            attack:str
            miss:str

            tap:str
            hold:str
            slide:str
            air:str
            flick:str

            icon_clear:str
            icon_rank:str
            icon_combo:str
            

        return SCORE_DETAILS(played,music_img,music_title,music_score,music_difficulty,character,skill,max_combo,critical_break,chunithm_break,hit,miss,tap,hold,slide,air,flick,icon_clear,icon_technical_rank,icon_combo)
        

    def get_all_music(self,difficulty:str="master"):
        if difficulty=="master":
            None
        elif difficulty=="expert":
            None
        elif difficulty=="advanced":
            None
        elif difficulty=="basic":
            None
        elif difficulty=="ultima":
            None
        else:
            raise CHUNITHMError("master / expert / advanced / basic / ultima から選んでください")
       
        music_genre=self.session.get(CHUNITHM_MOBILE+"record/musicGenre")
        music_token=BeautifulSoup(music_genre.content,"html.parser").find(type="hidden")["value"]
        self.session.post(CHUNITHM_MOBILE+"record/musicGenre/send"+difficulty,data={"genre":"99","token":music_token})
        all_music=self.session.get(CHUNITHM_MOBILE+"record/musicGenre/"+difficulty)
        soup=BeautifulSoup(all_music.content,"html.parser")
        musics=soup.find_all(action="https://new.chunithm-net.com/chuni-mobile/html/mobile/record/musicGenre/sendMusicDetail/")
        music_dict={}
        for music in musics:
            music_title=music.find(class_="music_title").text
            hiddens=music.find_all("input")
            
            idx=hiddens[0]["value"]
            genre=hiddens[1]["value"]
            diff=hiddens[2]["value"]
            token=hiddens[3]["value"]
            music_score=music.find(class_="play_musicdata_highscore")
            if music_score:
                music_score=music_score.find(class_="text_b").text
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
                music_score=None
            

            music_dict[music_title]={"diff":diff,"genre":genre,"idx":idx,"token":token,"score":music_score}
        
        return music_dict

    def get_history(self):
        history=self.session.get(CHUNITHM_MOBILE+"record/playlog")
        soup=BeautifulSoup(history.content,"html.parser")
        musics=soup.find_all(class_="frame02 w400")
        music_list=[]
        for music in musics:
            difpng=music.find(class_="play_track_result").find("img")["src"]
            if "master.png" in difpng:
                music_difficulty="Master"
            elif "expert.png" in difpng:
                music_difficulty="Expert"
            elif "ultima.png" in difpng:
                music_difficulty="Ultima"
            elif "advanced.png" in difpng:
                music_difficulty="Advanced"
            elif "basic.png" in difpng:
                music_difficulty="Basic"

            played=music.find(class_="play_datalist_date").text
            music_img=music.find(class_="play_jacket_img").find("img")["data-original"]
            music_title=music.find(class_="play_musicdata_title").text
            music_score=music.find(class_="play_musicdata_score_text").text
            icons=music.find(class_="play_musicdata_icon clearfix").find_all("img")
            if "icon_clear.png" in icons[0]["src"]:
                icon_clear=icons[0]["src"]
                icon_technical_rank=icons[1]["src"]
                if len(icons)==1:
                    icon_combo=None
                else:
                    icon_combo=icons[1]["src"]
                
            else:
                icon_clear=None
                icon_technical_rank=icons[0]["src"]
                if len(icons)==1:
                    icon_combo=None
                else:
                    icon_combo=icons[1]["src"] 
                
            hiddens=music.find_all("input")
            idx=hiddens[0]["value"]
            token=hiddens[1]["value"]
            music_list.append({"title":music_title,"difficulty":music_difficulty,"score":music_score,"score_int":int(music_score.replace(",","")),"img":music_img,"played":played,"idx":idx,"token":token})

        return music_list