import os
import json
import subprocess as sp
import sqlalchemy as sql
from sqlalchemy import Column, String, Integer, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .logger import Print
from .queueprocess import Threader
from .errors import SmsError

# create database file
Base = declarative_base()


class SQL(Base):
    __tablename__ = "messages"
    TIMEOUT = 60 * 2

    id = Column("id", Integer, unique=True, primary_key=True)
    threadid = Column("threadid", Integer, nullable=False)
    type = Column("type", String(10), nullable=False)
    read = Column("read", Boolean, nullable=False, default=True)
    sender = Column("sender", String(40), nullable=True, default="Unknown")
    number = Column("number", String(30), nullable=True, default="N/A")
    received = Column("received", String(30), nullable=False)
    body = Column("body", String(500), nullable=False)

    def __init__(self, database_uri="mysms.db"):
        engine = sql.create_engine("sqlite:///{}".format(database_uri))
        self.session = sessionmaker(bind=engine)
        self.metadata.create_all(bind=engine)


class SMS(SQL):
    def __init__(self):
        # create the table name to store the sms
        self.sms = self.text_message()
        super(SMS, self).__init__()

    @classmethod
    def text_message(cls, limit=5000, box="all"):
        """ 
            Retrieves text messages using android termux-api 

            :param limit:
                Number of text message to retrieve (default 5000)
        
            :param box:
                Type of text message to return 
                    all - returns outbox,inbox,and draft 
                    inbox  - return text messages from inbox only
                    outbox  - return text messages from outbox only
                    draft - return text messages from draft only
            :return dict:
        """
        # invoke termux sms api to generate the sms list
        cmd = "termux-sms-list -dl {} -nt {}".format(limit, box)

        try:
            sms = sp.check_output(cmd, shell=True, timeout=cls.TIMEOUT).decode("utf8")
        except sp.CalledProcessError as e:  # if termux-api is not install
            error = "Termux api not install or is an incompatible version"
            raise SmsError(1, error)
        except sp.TimeoutExpired:
            error = (
                "\nThere seem to be a problem while retrieving",
                "your text messages...Come back later or report this issue.",
            )
            raise SmsError(2, " ".join(error))

        except:
            raise SmsError(3, "Unable to create Sms database")

        # check whether text messages were populates
        if sms:
            sms = list(json.loads(sms))
            [text.update(id=count) for count, text in enumerate(sms, start=1)]
            return sms

    def create(self):
        """ Populate the database with the text messages"""
        session = self.session()  # inherited from SQL
        self.count = 1
        text = self.text_message()
        self.thread = Threader(self.run, text, session)
        self.thread.run()
        session.commit()

    def run(self, sms, session=None):  # sms is one sms at a time
        """ Populate the database with the text messages
            :param sms: text to put in database
                  type: dict 

            :param: session: sessionmaker object (pass only when threading')
                             by default, the class object will handle
                             the sessionmaker
                    default: None,
        """
        if not session:
            session = self.session
        sequel = SQL()
        setattr(sequel, "id", self.count)
        self.count += 1
        for k, v in sms.items():
            setattr(sequel, k, v)
            Print(k, v)
        session.add(sequel)


def main():
    try:
        SMS()
    except SmsError as e:
        Print(e)
        Print(
            "\nIf this issue presists, file a bug report here:",
            "\nhttps://github.com/cbedroid/termux-sqlsms/issues",
        )


if __name__ == "__main__":
    main()
