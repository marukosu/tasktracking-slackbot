import MySQLdb
 
class MySQL:

    def connect(self):
        conn = MySQLdb.connect(
                user='root',
                passwd='root',
                host='localhost',
                db='slack')
        return conn
    
    
    def showUsers(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("select * from users")
     
        for row in cursor.fetchall():
            print("ID:" + str(row[0]) + "  NAME:" + row[1])
     
        cursor.close
        conn.close
    
    def registerUser(self, id, name):
        conn = self.connect()
        cursor = conn.cursor()
     
        cursor.execute("insert into users (id, name) values (%s, %s) on duplicate key update name = %s", (id, name, name))
    
        conn.commit()
        cursor.close
        conn.close
    
    def registerTask(self, uid, taskName, startTime):
        conn = self.connect()
        cursor = conn.cursor()
    
        cursor.execute("insert into tasks (uid, name, start) values (%s, %s, %s)", (uid, taskName, startTime))
    
        conn.commit()
        cursor.close
        conn.close
    
    def finishTask(self, uid, taskName, endTime):
        conn = self.connect()
        cursor = conn.cursor()
    
        try:
            cursor.execute("select id from tasks where uid = %s and name = %s order by id desc limit 1", (uid, taskName))
            task = cursor.fetchone()
            if task is None:
                raise
            id = task[0]
            cursor.execute("update tasks set end = %s where id = %s", (endTime, id))
            conn.commit()
        except:
            conn.rollback()
            return -1
        
        finally:
            cursor.close
            conn.close
        
        return 0
    
    def getTaskList(self, uid, fromTime, toTime): 
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("select name, start, end from tasks where uid = %s and start > %s and (end < %s or end is NULL)", (uid, fromTime, toTime))
     
        for row in cursor.fetchall():
            print("Name:" + row[0] + "  Start:" + str(row[1]) + "  End:" + str(row[2]))
     
        cursor.close
        conn.close
    
 
