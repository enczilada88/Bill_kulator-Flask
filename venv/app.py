from flask import Flask, request, url_for, redirect, render_template, flash, g
import sqlite3
app=Flask(__name__)

app_info={
    'db_file':r'C:\Bill_kulator\bills.db'
}

app = Flask(__name__)
app.config['SECRET_KEY']='sfsfajkfjakfjalkjftygda'

def get_db():
    if not hasattr(g, 'sqlite_db'):
        conn=sqlite3.connect(app_info['db_file'])
        conn.row_factory=sqlite3.Row
        g.sqlite_db=conn
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


class Bill:
    def __init__(self, type_b, year_b, month_b, value_b, description_b):
        self.type_b=type_b
        self.year_b=year_b
        self.month_b=month_b
        self.value_b=value_b
        self.description_b=description_b
    def __repr__(self):
        return '<Bill {}>'.format(self.type_b)
    
class BillOverview:
    def __init__(self):
        self.bills=[]
        self.denied_type=[]
    def load_bill(self):
        self.bills.append(Bill('Phone', 2021, 12, 49, 'overdue'))
        self.bills.append(Bill('Electricity',2022,1,158,'ongoing'))
        self.bills.append(Bill('Phone', 2023, 1, 49, 'forecast'))
        self.denied_type.append('Gambling')
    def get_by_type(self, description_b):
        for bill in self.bills:
            if bill.description_b==description_b:
                return bill
        return Bill('n/a',9999,99,0,'n/a')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/links')
def links():
    body='''<a href="http://www.google.com" target="_blank">Google</a> <br>
    <a href="http://www.kuriergarwolinski.com" target="_blank">GGarwolin website</a> <br>
 
    '''
    return body

@app.route('/report_bill', methods=['GET','POST'])
def report_bill():
    overview=BillOverview()
    overview.load_bill()
    desc = ['ongoing', 'overdue', 'forecast']

    if request.method=='GET':
        return render_template('report_bill.html', overview=overview, desc=desc, active_menu='report_bill')
    else:

        type_b='Electricity'
        if 'type_b' in request.form:
            type_b=request.form['type_b']
            
        year_b=9999
        if 'year_b' in request.form:
            year_b=request.form['year_b']
            
        month_b=99
        if 'month_b' in request.form:
            month_b=request.form['month_b']
            
        value_b=0
        if 'value_b' in request.form:
            value_b=request.form['value_b']
            
        description_b='ongoing'
        if 'description_b' in request.form:
            description_b=request.form['description_b']
            
            
        if type_b in overview.denied_type:
            flash ('Gambing should not be reported here!')

        else:
            db=get_db()
            sql_command='insert into bills(type_b, year_b, month_b, value_b, description_b) values (?,?,?,?,?)'
            overview.load_bill()
            db.execute(sql_command,[type_b, year_b, month_b, value_b, description_b])
            db.commit()
            flash('Provided data of bills for {} was accepted'.format((type_b)))
    return render_template('report_bill_result.html', month_b=month_b,year_b=year_b,value_b=value_b, description_b=description_b, bill_info=overview.get_by_type(description_b), active_menu='report_bill')


@app.route('/bills')
def bills():
    db=get_db()
    sql_command='select id, type_b, year_b, month_b, value_b, description_b from bills;'
    cur=db.execute(sql_command)
    bills=cur.fetchall()

    return render_template('bills.html', bills=bills, active_menu='bills')

@app.route('/delete_bill/<int:bill_id>')
def delete_bill(bill_id):
    db=get_db()
    sql_statement='delete from bills where id=?;'
    db.execute(sql_statement,[bill_id])
    db.commit()
    return redirect(url_for(('bills')))



@app.route('/edit_bill/<int:bill_id>', methods=['GET','POST'])
def edit_bill(bill_id):
    overview=BillOverview()
    overview.load_bill()
    db=get_db()

    if request.method == 'GET':
        sql_statement='select id, type_b, year_b, month_b, value_b, description_b from bills where id=?;'
        cur = db.execute(sql_statement,[bill_id])
        bill=cur.fetchone()
        if bill==None:
            flash('No such bill!')
            return redirect(url_for('bills'))
        else:
            return render_template('edit_bill.html', bill=bill, overview=overview, active_menu='bills')



    else:
        type_b = 'Electricity'
        if 'type_b' in request.form:
            type_b = request.form['type_b']

        year_b = 9999
        if 'year_b' in request.form:
            year_b = request.form['year_b']

        month_b = 99
        if 'month_b' in request.form:
            month_b = request.form['month_b']

        value_b = 0
        if 'value_b' in request.form:
            value_b = request.form['value_b']

        description_b = 'ongoing'
        if 'description_b' in request.form:
            description_b = request.form['description_b']

        if type_b in overview.denied_type:
            flash('Gambing should not be reported here!')

        else:
            sql_command='''
            update bills set type_b=?, year_b=?, month_b=?, value_b=?, description_b=? where id=?'''
            db.execute(sql_command, [type_b, year_b, month_b, value_b, description_b, bill_id])
            db.commit()
            flash('Bill was updated')

    return redirect(url_for('bills'))







if __name__=='__main__':
    app.run()