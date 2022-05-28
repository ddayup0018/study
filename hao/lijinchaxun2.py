from pywebio import *
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
import pandas as pd
import os
import datetime

def check_input(a):
    if len(a) < 6:
        return '太短,至少6位'
    if len(a)>12:
        return '太长了大哥,能记住不'
# 新用户注册
def new_user():
    global user_name
    inputs_new=input_group(
        label='用户注册,并且录入一张表格!',
        inputs=[
            input('用户名',name='user_name',validate=check_input),
            input('密码',name='password',type=PASSWORD,validate=check_input),
            input('确认密码',name='check_password',type=PASSWORD,
                  placeholder='请保持两次输入密码一致!'),
            file_upload('请录入一张表格',accept=['.xls','.xlsx'],required=True,
                        name='user_excel',help_text='必须是excel表格')
        ]
    )
    user_name=inputs_new['user_name']
    password=inputs_new['password']
    check_password=inputs_new['check_password']
    user_excel=inputs_new['user_excel']

    if password != check_password:
        toast('两次输入密码不一致')
        return new_user()

    if not('.xlsx' in user_excel['filename'] or '.xls' in user_excel['filename']):
        toast('录入的表格类型错误')
        return new_user()

    table_user = pd.read_excel('用户信息表.xlsx')
    if user_name in list(table_user['用户名']):
        toast('用户名已存在')
        return new_user()

    # 保存用户录入的表格
    table=pd.read_excel(user_excel['content'])
    file_name=user_excel['filename'].split('.')
    table.to_excel(f'./用户查询表/{user_name}.xlsx',sheet_name=file_name[0]
                   ,index=False)

    # 添加新用户信息
    djtime = datetime.datetime.now()
    table_user=table_user.append({'用户名':user_name,'密码':password,'登记时间':djtime},ignore_index=True)
    table_user.to_excel('用户信息表.xlsx',index=False)
    toast('注册成功')
    select_name()

# 老用户登录
def old_user():
    global user_name
    inputs_old=input_group(
        label='用户登录!',
        inputs=[
            input('用户名',name='user_name',validate=check_input),
            input('密码',name='password',type=PASSWORD,validate=check_input)
        ]
    )
    user_name=inputs_old['user_name']
    password=inputs_old['password']

    table_user = pd.read_excel('用户信息表.xlsx',dtype={'密码':str})
    sel_password=table_user.loc[table_user['用户名']==user_name,'密码'].values[0]

    if user_name in list(table_user['用户名']):
        if sel_password == password:
            user_manage()
        else:
            toast('密码错误!')
            return old_user()
    else:
        toast('用户不存在')
    return old_user()

# 用户管理
def user_manage():
    manage_choice = select('请选择用户管理类型', options=['查询姓名', '查看表格','下载表格','删除表格'],
                          help_text='默认为姓名查询')
    if manage_choice == '查询姓名':
        select_name()
    elif manage_choice == '查看表格':
        select_all()
    elif manage_choice == '下载表格':
        download_excel()
    elif manage_choice == '删除表格':
        delete_excel()
    else:
        select_name()

def excel_exist(fun):
    def inner():
        if not os.path.exists(f'./用户查询表/{user_name}.xlsx'):
            toast('你的表格不存在')
        else:
            fun()
    return inner

# 查询姓名
@excel_exist
def select_name():
    sel_name=input('请输入要查询人的姓名')
    select_table = pd.read_excel(f'./用户查询表/{user_name}.xlsx')
    select_table.index += 1
    if sel_name in list(select_table['姓名']):
        result=select_table.loc[select_table['姓名']==sel_name]
        popup(title='查询结果',content=put_html(result))
    else:
        toast('这个人并没有斗人亲')
    return select_name()

# 查看表格
@excel_exist
def select_all():
    pd.set_option('display.max_rows',None)
    select_table = pd.read_excel(f'./用户查询表/{user_name}.xlsx')
    select_table.index +=1
    popup(title='查询结果',content=put_html(select_table))
    return user_manage()

# 下载表格
@excel_exist
def download_excel():
    down = open(f'./用户查询表/{user_name}.xlsx','rb').read()
    download(name=f'{user_name}.xlsx',content=down)
    return user_manage()

# 删除表格
@excel_exist
def delete_excel():
    # 删除用户表
    os.remove(f'./用户查询表/{user_name}.xlsx')
    # 删除信息表的账号和密码
    delete_table = pd.read_excel('./用户信息表.xlsx')
    delete=delete_table[delete_table['用户名']==user_name].index.tolist()[0]
    delete_table.drop(index=delete,inplace=True)
    delete_table.to_excel('./用户信息表.xlsx',index=False)
    toast('删除成功,账号和表格被永久删除!')
    return do_choice()

def do_choice():
    rad_choice = radio('请输入用户类型', options=['新用户', '老用户'])
    if rad_choice == '新用户':
        new_user()
    elif rad_choice== '老用户':
        old_user()
    else:
        toast('请选择一个身份')
        return do_choice()

def main():
    set_env(title='礼金查询工具')
    put_markdown('## 礼金查询工具低调版')
    put_markdown("""
    ### 使用说明:
    ##### 1. 新用户注册账号用于下一次查询和需录入一张自己的礼金excel表格,格式为".xlsx"或".xls";
    ##### 2. 老用户直接登录账号即可按姓名查询 查看表格 下载表格 删除信息!
    ##### 3. 本工具为测试学习用,为了您的数据安全,请备份好您的数据!
    """
    )
    put_markdown('###### 表格样式:')
    img=open('格式图片.png', 'rb').read()
    put_image(img,title='表格样式')
    down = open('表格模板.xlsx','rb').read()
    put_file(name='表格模板.xlsx',content=down,label='下载表格模板')
    do_choice()

if __name__ == '__main__':
    start_server(main,8000)
