from flask import Flask, request, g
from flask import current_app, render_template
from flask import url_for, redirect
import datetime


def create_app():
    app = Flask("project")
    app.config.from_mapping(DATABASE='project')

    from . import db

    @app.route('/')
    @app.route('/sign_in', methods=['GET', 'POST'])
    def sign_in():
        msg = ''
        if request.method == "POST" and 'email' in request.form and 'pwd' in request.form:
            username = request.form.get('email')
            password = request.form.get('pwd')
            conn = db.get_db()
            cur = conn.cursor()

            cur.execute(
                "select id from users where username=%s and password=%s", (username, password))
            id = cur.fetchone()[0]
            if id:
                msg = 'login success'
                cur.execute(
                    f"select pn.poll_id,pn.poll_name from users u,poll_names pn,poll_user up where u.id=up.user_id and pn.poll_id=up.poll_id and up.user_id={id}")
                pole_list = cur.fetchall()
                pid, pole_name = [], []
                for row in pole_list:
                    pid.append(row[0])
                    pole_name.append(row[1])

                data = dict(
                    pole_name=pole_name,
                    pid=pid,
                    len=len(pid),
                    uid=id)
                return render_template('pl_list.html', **data)

            else:
                msg = 'incorrect username/password'
        elif request.method == "GET":
            return render_template('login.html', msg=msg)

    @app.route('/sign_up', methods=['GET', 'POST'])
    def sign_up():
        msg = ''
        if request.method == "POST" and 'email' in request.form and 'pwd' in request.form and 'rpwd' in request.form:
            username = request.form.get('email')
            password = request.form.get('pwd')
            re_enter_password = request.form.get('rpwd')
            conn = db.get_db()
            cur = conn.cursor()
            if not password == re_enter_password:
                msg = 'incorrect password '
            else:

                cur.execute(
                    "select * from users where username=%s", (username,))
                id = cur.fetchone()
                if id:
                    msg = 'username already taken'
                else:
                    cur.execute(
                        "insert into users(username,password) values(%s,%s)", (username, password))
                    conn.commit()

                    msg = 'registration success'

        return render_template('reg.html', msg=msg)

    @app.route('/create', methods=['GET', 'POST'])
    def create():
        msg = ''

        if request.method == "POST" and 'pn' in request.form and 'ques' in request.form and 'opt[]' in request.form:

            uid = request.args['uid']
            opts = request.form.getlist('opt[]')
            pn = request.form.get('pn')
            ques = request.form.get('ques')

            conn = db.get_db()
            cur = conn.cursor()
            cur.execute(
                "insert into poll_names(poll_name,question) values (%s,%s) ", (pn, ques,))
            conn.commit()
            cur.execute(
                "select max(poll_id ) from poll_names")
            p_id = cur.fetchone()[0]

            cur.execute(
                "insert into poll_user values(%s,%s)", (uid, p_id,))
            for opt in opts:
                cur.execute(
                    "insert into poll_results values(%s,%s)", (p_id, opt))
            conn.commit()

            cur.execute(
                "select count(poll_id) from poll_user where user_id=%s", (uid,))
            l = cur.fetchone()[0]
            cur.execute(
                f"select pn.poll_id,pn.poll_name from users u,poll_names pn,poll_user up where u.id=up.user_id and pn.poll_id=up.poll_id and up.user_id={uid}")
            pole_list = cur.fetchall()
            pid, pole_name = [], []
            for row in pole_list:
                pid.append(row[0])
                pole_name.append(row[1])
            return render_template('pl_list.html', pid=pid, len=l, pole_name=pole_name, p_id=p_id, uid=uid)

        elif request.method == "GET":
            uid = request.args['uid']

            return render_template('create.html', uid=uid)

        else:
            msg = "Fill the form"
            uid = request.args['uid']
            return render_template('create.html', msg=msg, uid=uid)

    @app.route('/share', methods=["GET", "POST"])
    def share():
        msg = ''
        if request.method == "POST" and 'poll' in request.form:
            poll = request.form['poll']
            p_id = request.args['p_id']
            conn = db.get_db()
            cur = conn.cursor()
            cur.execute("insert into poll_results values(%s,%s)",
                        (p_id, poll,))
            conn.commit()

            return render_template('tq.html')

        elif request.method == "GET":
            p_id = request.args['p_id']
            conn = db.get_db()
            cur = conn.cursor()
            cur.execute(
                "select poll_name,question from poll_names where poll_id=%s", (p_id, ))
            pd = cur.fetchone()
            pn, ques = pd[0], pd[1]
            cur.execute(
                "select distinct(ans) from poll_results where poll_id=%s", (p_id,))
            ans = [x[0] for x in cur.fetchall()]
            data = dict(
                ans=ans,
                pn=pn,
                ques=ques,
                msg=msg,
                p_id=p_id
            )
            return render_template('share.html', **data)

        else:
            msg = "select an option"

    @app.route('/results', methods=["GET"])
    def results():
        p_id = request.args['p_id']

        if request.method == "GET":
            conn = db.get_db()
            cur = conn.cursor()
            cur.execute(
                "select distinct ans from poll_results where poll_id=%s", (p_id,))
            nam = [x[0] for x in cur.fetchall()]
            cur.execute(
                "select count(ans) from poll_results where poll_id=%s group by ans ", (p_id,))
            val = [x[0]-1 for x in cur.fetchall()]
            l = len(nam)
        return render_template('results.html', nam=nam, val=val, l=l)

    return app
