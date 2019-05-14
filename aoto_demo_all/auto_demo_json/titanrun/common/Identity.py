#coding=utf-8
import random
import re
import string
import sys
from datetime import date
from datetime import timedelta
from datetime import datetime
from titanrun.config.DistrictsAll import Districts
import time
import hashlib
import base64
import os

reload(sys)
sys.setdefaultencoding('utf-8')

def generate_name():
        a1 = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王', '冯', '陈', '褚', '卫', '蒋', '沈', '韩', '杨', '朱', '秦', '尤', '许',
                '何', '吕', '施', '张', '孔', '曹', '严', '华', '金', '魏', '陶', '姜', '戚', '谢', '邹', '喻', '柏', '水', '窦', '章',
                '云', '苏', '潘', '葛', '奚', '范', '彭', '郎', '鲁', '韦', '昌', '马', '苗', '凤', '花', '方', '俞', '任', '袁', '柳',
                '酆', '鲍', '史', '唐', '费', '廉', '岑', '薛', '雷', '贺', '倪', '汤', '滕', '殷', '罗', '毕', '郝', '邬', '安', '常',
                '乐', '于', '时', '傅', '皮', '卞', '齐', '康', '伍', '余', '元', '卜', '顾', '孟', '平', '黄', '和', '穆', '萧', '尹',
                '姚', '邵', '堪', '汪', '祁', '毛', '禹', '狄', '米', '贝', '明', '臧', '计', '伏', '成', '戴', '谈', '宋', '茅', '庞',
                '熊', '纪', '舒', '屈', '项', '祝', '董', '梁']
        a2 = ['的', '一', '是', '了', '我', '不', '人', '在', '他', '有', '这', '个', '上', '们', '来', '到', '时', '大', '地', '为',
                       '子', '中', '你', '说', '生', '国', '年', '着', '就', '那', '和', '要', '她', '出', '也', '得', '里', '后', '自', '以',
                       '会', '家', '可', '下', '而', '过', '天', '去', '能', '对', '小', '多', '然', '于', '心', '学', '么', '之', '都', '好',
                       '看', '起', '发', '当', '没', '成', '只', '如', '事', '把', '还', '用', '第', '样', '道', '想', '作', '种', '开', '美',
                       '总', '从', '无', '情', '己', '面', '最', '女', '但', '现', '前', '些', '所', '同', '日', '手', '又', '行', '意', '动',
                       '方', '期', '它', '头', '经', '长', '儿', '回', '位', '分', '爱', '老', '因', '很', '给', '名', '法', '间', '斯', '知',
                       '世', '什', '两', '次', '使', '身', '者', '被', '高', '已', '亲', '其', '进', '此', '话', '常', '与', '活', '正', '感',
                       '见', '明', '问', '力', '理', '尔', '点', '文', '几', '定', '本', '公', '特', '做', '外', '孩', '相', '西', '果', '走',
                       '将', '月', '十', '实', '向', '声', '车', '全', '信', '重', '三', '机', '工', '物', '气', '每', '并', '别', '真', '打',
                       '太', '新', '比', '才', '便', '夫', '再', '书', '部', '水', '像', '眼', '等', '体', '却', '加', '电', '主', '界', '门',
                       '利', '海', '受', '听', '表', '德', '少', '克', '代', '员', '许', '稜', '先', '口', '由', '死', '安', '写', '性', '马',
                       '光', '白', '或', '住', '难', '望', '教', '命', '花', '结', '乐', '色', '更', '拉', '东', '神', '记', '处', '让', '母',
                       '父', '应', '直', '字', '场', '平', '报', '友', '关', '放', '至', '张', '认', '接', '告', '入', '笑', '内', '英', '军',
                       '候', '民', '岁', '往', '何', '度', '山', '觉', '路', '带', '万', '男', '边', '风', '解', '叫', '任', '金', '快', '原',
                       '吃', '妈', '变', '通', '师', '立', '象', '数', '四', '失', '满', '战', '远', '格', '士', '音', '轻', '目', '条', '呢',
                       '病', '始', '达', '深', '完', '今', '提', '求', '清', '王', '化', '空', '业', '思', '切', '怎', '非', '找', '片', '罗',
                       '钱', '紶', '吗', '语', '元', '喜', '曾', '离', '飞', '科', '言', '干', '流', '欢', '约', '各', '即', '指', '合', '反',
                       '题', '必', '该', '论', '交', '终', '林', '请', '医', '晚', '制', '球', '决', '窢', '传', '画', '保', '读', '运', '及',
                       '则', '房', '早', '院', '量', '苦', '火', '布', '品', '近', '坐', '产', '答', '星', '精', '视', '五', '连', '司', '巴',
                       '奇', '管', '类', '未', '朋', '且', '婚', '台', '夜', '青', '北', '队', '久', '乎', '越', '观', '落', '尽', '形', '影',
                       '红', '爸', '百', '令', '周', '吧', '识', '步', '希', '亚', '术', '留', '市', '半', '热', '送', '兴', '造', '谈', '容',
                       '极', '随', '演', '收', '首', '根', '讲', '整', '式', '取', '照', '办', '强', '石', '古', '华', '諣', '拿', '计', '您',
                       '装', '似', '足', '双', '妻', '尼', '转', '诉', '米', '称', '丽', '客', '南', '领', '节', '衣', '站', '黑', '刻', '统',
                       '断', '福', '城', '故', '历', '惊', '脸', '选', '包', '紧', '争', '另', '建', '维', '绝', '树', '系', '伤', '示', '愿',
                       '持', '千', '史', '谁', '准', '联', '妇', '纪', '基', '买', '志', '静', '阿', '诗', '独', '复', '痛', '消', '社', '算',
                       '义', '竟', '确', '酒', '需', '单', '治', '卡', '幸', '兰', '念', '举', '仅', '钟', '怕', '共', '毛', '句', '息', '功',
                       '官', '待', '究', '跟', '穿', '室', '易', '游', '程', '号', '居', '考', '突', '皮', '哪', '费', '倒', '价', '图', '具',
                       '刚', '脑', '永', '歌', '响', '商', '礼', '细', '专', '黄', '块', '脚', '味', '灵', '改', '据', '般', '破', '引', '食',
                       '仍', '存', '众', '注', '笔', '甚', '某', '沉', '血', '备', '习', '校', '默', '务', '土', '微', '娘', '须', '试', '怀',
                       '料', '调', '广', '蜖', '苏', '显', '赛', '查', '密', '议', '底', '列', '富', '梦', '错', '座', '参', '八', '除', '跑',
                       '亮', '假', '印', '设', '线', '温', '虽', '掉', '京', '初', '养', '香', '停', '际', '致', '阳', '纸', '李', '纳', '验',
                       '助', '激', '够', '严', '证', '帝', '饭', '忘', '趣', '支', '春', '集', '丈', '木', '研', '班', '普', '导', '顿', '睡',
                       '展', '跳', '获', '艺', '六', '波', '察', '群', '皇', '段', '急', '庭', '创', '区', '奥', '器', '谢', '弟', '店', '否',
                       '害', '草', '排', '背', '止', '组', '州', '朝', '封', '睛', '板', '角', '况', '曲', '馆', '育', '忙', '质', '河', '续',
                       '哥', '呼', '若', '推', '境', '遇', '雨', '标', '姐', '充', '围', '案', '伦', '护', '冷', '警', '贝', '著', '雪', '索',
                       '剧', '啊', '船', '险', '烟', '依', '斗', '值', '帮', '汉', '慢', '佛', '肯', '闻', '唱', '沙', '局', '伯', '族', '低',
                       '玩', '资', '屋', '击', '速', '顾', '泪', '洲', '团', '圣', '旁', '堂', '兵', '七', '露', '园', '牛', '哭', '旅', '街',
                       '劳', '型', '烈', '姑', '陈', '莫', '鱼', '异', '抱', '宝', '权', '鲁', '简', '态', '级', '票', '怪', '寻', '杀', '律',
                       '胜', '份', '汽', '右', '洋', '范', '床', '舞', '秘', '午', '登', '楼', '贵', '吸', '责', '例', '追', '较', '职', '属',
                       '渐', '左', '录', '丝', '牙', '党', '继', '托', '赶', '章', '智', '冲', '叶', '胡', '吉', '卖', '坚', '喝', '肉', '遗',
                       '救', '修', '松', '临', '藏', '担', '戏', '善', '卫', '药', '悲', '敢', '靠', '伊', '村', '戴', '词', '森', '耳', '差',
                       '短', '祖', '云', '规', '窗', '散', '迷', '油', '旧', '适', '乡', '架', '恩', '投', '弹', '铁', '博', '雷', '府', '压',
                       '超', '负', '勒', '杂', '醒', '洗', '采', '毫', '嘴', '毕', '九', '冰', '既', '状', '乱', '景', '席', '珍', '童', '顶',
                       '派', '素', '脱', '农', '疑', '练', '野', '按', '犯', '拍', '征', '坏', '骨', '余', '承', '置', '臓', '彩', '灯', '巨',
                       '琴', '免', '环', '姆', '暗', '换', '技', '翻', '束', '增', '忍', '餐', '洛', '塞', '缺', '忆', '判', '欧', '层', '付',
                       '阵', '玛', '批', '岛', '项', '狗', '休', '懂', '武', '革', '良', '恶', '恋', '委', '拥', '娜', '妙', '探', '呀', '营',
                       '退', '摇', '弄', '桌', '熟', '诺', '宣', '银', '势', '奖', '宫', '忽', '套', '康', '供', '优', '课', '鸟', '喊', '降',
                       '夏', '困', '刘', '罪', '亡', '鞋', '健', '模', '败', '伴', '守', '挥', '鲜', '财', '孤', '枪', '禁', '恐', '伙', '杰',
                       '迹', '妹', '藸', '遍', '盖', '副', '坦', '牌', '江', '顺', '秋', '萨', '菜', '划', '授', '归', '浪', '听', '凡', '预',
                       '奶', '雄', '升', '碃', '编', '典', '袋', '莱', '含', '盛', '济', '蒙', '棋', '端', '腿', '招', '释', '介', '烧', '误',
                       '乾', '坤']
        a3 = ['', '立', '国', '哲', '彦', '振', '海', '正', '志', '子', '晋', '自', '怡', '德', '赫', '君', '平', '永', '贞', '咏', '德',
              '宇', '寰', '雨', '泽', '玉', '韵', '越', '彬', '蕴', '和']
        name = random.choice(a1) + random.choice(a2) + random.choice(a3)+ random.choice(a2) + random.choice(a2)+ random.choice(a2)
        return unicode(name)

def generate_phone():
    prelist = ["130", "131", "132", "133", "134", "135", "136", "137", "138", "139", "147", "150", "151", "152",
                   "153", "155", "156", "157", "158", "159", "186", "187", "188"]
    phone=random.choice(prelist) + "".join(random.choice("0123456789") for i in range(8))
    return unicode(phone)

def generate_mail():
    mail = string.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a'], 3)).replace(' ', '') + '_' + generate_phone() + '@cmrh.com'
    return mail

def get_district_code():
    districtlist = Districts.keys()
    districtlist.sort()
    codelist0 = []
    for code in districtlist:
        if code[2:4] != '00' and code[4:6] != '00':
            codelist0.append(code)
    return codelist0

def generate_id(bir='19800101', sex='1',idtype='01'):
    # idtype:
    # 01 - 居民身份证
    # 02 - 居民户口薄
    # 04 - 军人身份证
    # 11 - 港澳台居民往来内地通行证
    # 12 - 出生证
    # 51 - 外国护照
    # 98 - 武警身份证
    # 99 - 其他证件
    # sex:
    # 1-男性
    # 2-女性
    id = u''
    try:
        if idtype=='01':
            while id == u'':
                codelist0 = get_district_code()
                id = codelist0[random.randint(0, len(codelist0))]  # 地区项
                if bir!='':
                    # 固定生日
                    id = id + bir
                else:
                    id = id + str(random.randint(1970, 1999))  # 年份项 ，修改上限，保证大于18岁
                    da = date.today() + timedelta(days=random.randint(1, 366))  # 月份和日期项
                    id = id + da.strftime('%m%d')
                if (sex == '1'):
                    # 固定性别：男
                    se = 2 * (random.randint(50, 150)) - 1
                elif (sex == '2'):
                    se = 2 * (random.randint(50, 150))
                else:
                    se = random.randint(100, 300)
                id = id + str(se)
                i = 0
                count = 0
                weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]  # 权重项
                checkcode = {'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8', '5': '7', '6': '6', '7': '5', '8': '5',
                             '9': '3', '10': '2'}  # 校验码映射
                for i in range(0, len(id)):
                    count = count + int(id[i]) * weight[i]
                id = id + checkcode[str(count % 11)]  # 算出校验码
                if (check_idcard(id)):
                    break
                else:
                    id = u''
        elif idtype=='11':
            id='C'+str(random.randint(10000000, 99999999))
        elif idtype=='12':
            codelist0 = get_district_code()
            district = codelist0[random.randint(0, len(codelist0))]  # 地区项
            id='H'+district[0:2]+ str(random.randint(1000000, 9999999))
        elif idtype == '51':
            id = 'G' + str(random.randint(10000000, 99999999))
    finally:
        return unicode(id)

def check_idcard(idcard):
    Errors = ['验证通过!', '身份证号码位数不对!', '身份证号码出生日期超出范围或含有非法字符!', '身份证号码校验错误!', '身份证地区非法!']
    area = {"11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古", "21": "辽宁", "22": "吉林", "23": "黑龙江",
            "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东", "41": "河南",
            "42": "湖北", "43": "湖南", "44": "广东", "45": "广西", "46": "海南", "50": "重庆", "51": "四川", "52": "贵州",
            "53": "云南", "54": "西藏", "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆", "71": "台湾",
            "81": "香港", "82": "澳门", "91": "国外"}
    idcard = str(idcard)
    idcard = idcard.strip()
    idcard_list = list(idcard)

    # 地区校验
    if (not area[(idcard)[0:2]]):
        print Errors[4]
    # 15位身份号码检测
    if (len(idcard) == 15):
        if ((int(idcard[6:8]) + 1900) % 4 == 0 or (
                            (int(idcard[6:8]) + 1900) % 100 == 0 and (int(idcard[6:8]) + 1900) % 4 == 0)):
            erg = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}$')  # //测试出生日期的合法性
        else:
            ereg = re.compile(
                '[1-9][0-9]{5}[0-9]{2}((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}$')  # //测试出生日期的合法性
        if (re.match(ereg, idcard)):
            # print Errors[0]
            return True
        else:
            # print Errors[2]
            return False
    # 18位身份号码检测
    elif (len(idcard) == 18):
        # 出生日期的合法性检查
        # 闰年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))
        # 平年月日:((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))
        if (int(idcard[6:10]) % 4 == 0 or (int(idcard[6:10]) % 100 == 0 and int(idcard[6:10]) % 4 == 0)):
            ereg = re.compile(
                '[1-9][0-9]{5}(19[0-9]{2}|20[0-9]{2})((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|[1-2][0-9]))[0-9]{3}[0-9Xx]$')  # //闰年出生日期的合法性正则表达式
        else:
            ereg = re.compile(
                '[1-9][0-9]{5}(19[0-9]{2}|20[0-9]{2})((01|03|05|07|08|10|12)(0[1-9]|[1-2][0-9]|3[0-1])|(04|06|09|11)(0[1-9]|[1-2][0-9]|30)|02(0[1-9]|1[0-9]|2[0-8]))[0-9]{3}[0-9Xx]$')  # //平年出生日期的合法性正则表达式
        # //测试出生日期的合法性
        if (re.match(ereg, idcard)):
            # //计算校验位
            S = (int(idcard_list[0]) + int(idcard_list[10])) * 7 + (int(idcard_list[1]) + int(
                idcard_list[11])) * 9 + (int(idcard_list[2]) + int(idcard_list[12])) * 10 + \
                (int(idcard_list[3]) + int(idcard_list[13])) * 5 + (int(idcard_list[4]) + int(
                idcard_list[14])) * 8 + (int(idcard_list[5]) + int(idcard_list[15])) * 4 + \
                (int(idcard_list[6]) + int(idcard_list[16])) * 2 + int(idcard_list[7]) * 1 + int(
                idcard_list[8]) * 6 + int(idcard_list[9]) * 3
            Y = S % 11
            M = "F"
            JYM = "10X98765432"
            M = JYM[Y]  # 判断校验位
            if (M == idcard_list[17]):  # 检测ID的校验位
                return True
            else:
                return False
        else:
            return False
    else:
        return False

# 根据ID获取身份证持有人的出生地所在地区
def get_district_by_id(ID,province="",city="",district="",detail=""):
    if (province=='' or city=='' or district=='') and len(ID)==18:
        ID_district = ID[0:6]
        ID_province = ID_district[0:2]
        ID_city = ID_district[0:4]
        province=ID_province + '0000'
        city = ID_city + '00'
        district = ID_district
    if province=='':
        province = '110000'
    if city == '':
        city = '110100'
    if district == '':
        district = '110101'
    if detail=='' or detail=='新闻路111号':
        detail = u'新闻路' + str(random.randint(1, 200)) + u'号'
    return (unicode(province), unicode(city), unicode(district), unicode(detail))

# 根据ID获取出生年月
def get_birthday_by_id(ID,bir=""):
    if bir=='' and len(ID)==18:
        bir = ID[6:14]
    year = bir[0:4]
    month = bir[4:6]
    day = bir[6:8]
    return unicode(year + '-' + month + '-' + day)


# 根据ID获取性别
def get_gender_by_id(ID,sex=""):
    if sex=='' and len(ID)==18:
        sex = ID[14:17]
    if int(sex) % 2 == 0:
        return u'女性'
    else:
        return u'男性'

    
def md5_format(net_key, s):
    m = hashlib.md5()  # 创建md5对象
    m.update(net_key + s)  # 生成加密串，其中net_key是密钥，s是普通字符串
    s = m.hexdigest().upper()
    return str(s)
 
def get_timestamp():
    t=time.time()
    #print int(round(t * 1000))
    return str(int(round(t * 1000)))
    


# 根据ID获取性别--返回 1-男 2-女
def get_gendercode_by_id(ID):
    ID_sex = ID[14:17]
    if int(ID_sex) % 2 == 0:
        return 2
    else:
        return 1


# 随机生成No,title表示流水号需要以什么固定字符串开头，没有传空字符串
# flag表示流水号里面是否需要拼上年月日，如果需要，则flag传Y;
# length表示流水号总长度减去开头固定字符和年月日的长度后，需要随机生成的位数
# 比如需要生成T2018050800002475124，get_no(11,'T','Y')
def get_no(length=6, title="A000000999",flag='N'):
    trans_date=""
    if flag=="Y":
        trans_date =datetime.now().strftime("%Y%m%d")
    random_no = "".join(str(random.choice(range(10))) for i in range(int(length)))
    return title + trans_date+random_no


def get_bar_code(doc_type,version = '01'):
    substring = doc_type + version + str(random.randint(10000000, 99999999))
    list = map(str, substring)
    sum = 0
    for num in list:
        sum += ord(num)
    mod = sum % 43
    if mod < 10:
        mod = '0' + str(mod)
    else:
        mod = str(mod)
    barcode = substring + mod
    return unicode(barcode)

    
#获取随机图片base64编码
def get_image_base64encode():
    form_list = ['.jpg','.png','.bmp','.gif']
    path = os.path.abspath('../..') + '\\' + 'image'
    for form in form_list:
        #image = 'image_00' + str(random.randint(0, 4)) + form
        image_path = path + '\\' + 'image_00' + str(random.randint(1, 4)) + form
        if os.path.exists(image_path):
            try:
                fp = open(image_path, 'rb')  # 二进制方式打开图文件
                ls_f = base64.b64encode(fp.read())  # 读取文件内容，转换为base64编码
                fp.close()
                return 'data:image/jpeg;base64,' + ls_f
            except Exception as e:
                return e.message
        else:
            raise Exception("文件格式不存在")

def g_random(sval):
    """
    根据需要，返回随机字符串
    :param sval: 例如
                $g_random$(t001,3,4,Y)  输出t001qPS005720181107   含义t001开头+3个随机字母+4个随机数字+日期
                $g_random$(s=T001,a=2,n=3,flag=Y)  输出T001UN00120181107  
                $g_random$(T001,a=2,n=3,flag=Y)    输出T001Bs82720181107
                $g_random$(T001,2,n=3,flag=Y)  输出T001nH27620181107
                $g_random$  输出A000000999821889  含义默认字符
                $g_random$(s=t001,flag=Y,n=5)  输出t0012018110772338  含义t001开头+日期+5个随机字母
                将需要写在括号里,括号里的需求依次拼接字符串，s,a,n,flag顺序自定义
                支持$g_random$(s,a,n,flag)
                支持$g_random$(s=T001,a=3,n=4,flag=Y)
                支持$g_random$(T001,a=3,4,flag=Y)
                支持三种模式，即纯value模式，key value模式，混合模式
                参数缺省，s表示字符串，a表示字母，n表示数字,flag表示特殊的字符，值可填Y，等号后面为个数
                可实现纯数字，纯字母，数字拼接字母混合，指定字符，当期日期
    :return: 目标字符串
    """
    result = ""
    if "$g_random$" == sval.split("*")[0]:
            result = get_no()
    elif "$g_random$" in sval:
        sval = sval.split("*")[0].replace("$g_random$(","")
        sval = sval.split("*")[0].replace(")","")
        temp_list = sval.split(",")
        for i in range(len(temp_list)):
            if "=" in temp_list[i]:
                key, length = temp_list[i].split("=")
                if key.upper() == "S":
                    result = result + length
                elif key.upper() == "A":
                    result = result + "".join([random.choice(string.ascii_letters) for x in range(int(length))])
                elif key.upper() == "N":
                    result = result + "".join(str(random.choice(range(10))) for x in range(int(length)))
                elif key.upper() == "FLAG":
                    if length.upper() == "Y":
                        result = result + time.strftime("%Y%m%d", time.localtime())
            else:
                if i == 0:
                    result = result + temp_list[i]
                elif i == 1:
                    result = result + "".join(
                        [random.choice(string.ascii_letters) for x in range(int(temp_list[i]))])
                elif i == 2:
                    result = result + "".join(str(random.choice(range(10))) for x in range(int(temp_list[i])))
                elif i == 3:
                    if temp_list[i].upper() == "Y":
                        result = result + time.strftime("%Y%m%d", time.localtime())
    return result




if __name__ == '__main__':
    # a = generate_id(bir='', sex='3', idtype='01')
    # print a
    # print get_birthday_by_id(a)
    # print get_gendercode_by_id(a)
    print get_no(6, "B000000999")




