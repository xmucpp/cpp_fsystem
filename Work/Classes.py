# -*- coding: utf-8 -*-
# @Time  : 2017/3/25 11:54
# @Author: FSOL
# @File  : Classes.py


class Function:
    def __init__(self, argu_num, dis_mode, way_to_use='', help_info='', module=''):
        self.module = module
        self.way_to_use =way_to_use
        self.help_info = help_info
        self.argu_num = argu_num
        self.dis_mode = dis_mode


class Connection:
    def __init__(self, fileno, socket, time, level='Unidentified'):
        self.fileno = fileno
        self.socket = socket
        self.level = level
        self.time = time

    def disconnect(self):
        """
        Standard way to disconnect and clean all stuff without risk.
        :param self:
        :return:
        """
        logger.info('{}:----{} disconnected'.format(self.fileno, self.level))
        if self.level == 'Unidentified':
            gv.outside.modify(self.fileno, 0)
        else:
            gv.inside.modify(self.fileno, 0)
        self.socket.close()
        gv.connections.pop(self.fileno)
        punish_list[self.fileno] = 0

    def save_send(self, message):
        """
        Standard way to send message.
        Avoid the risk of socket closed before send.(In that case, log and disconnect with it)
        :param self:
        :param message:
        :return: 0 for normal and 1 for error.
        """
        try:
            self.socket.sendall(message)
        except Exception:
            logger.warning("{}: close before send.".format(self.fileno))
            disconnect(self.fileno)
            return 1
        return 0

    def upgrade(self, level):
        """
        Give the connection level after received corresponding password.(Disconnect if it closed while logging or sending)
        :param self:
        :param level:
        :return:
        """
        self.level = level
        gv.inside.register(self.fileno, select.EPOLLIN)
        gv.outside.modify(self.fileno, 0)
        if self.save_send(cf.CONNECTSUCCESS) == 1:
            return 1
        try:
            logger.info('{}: {}----{} connected'.format(
                self.fileno, self.socket.getpeername(), self.level))
        except Exception:
            logger.warning("{}: unexcepted close.".format(self.fileno))
            self.disconnect()
        return 0


class Mission:
    def __init__(self, state, hour, minute, event):
        self.state = state
        self.hour = hour
        self.minute = minute
        self.event = event

class Worker:
    def __init__(self, event, table, state):
        self.event = event
        self.table = table
        self.state = state


# thanks for xjlin for his logger!
class Logger(object):
    """configure for logger"""
    def __init__(self, log_name, file_level, size=1024*1024, count=10):
        """init for logger"""
        self.logger = logging.getLogger(log_name)
        self.log_name = '{}.log'.format(log_name)
        self.log_file = os.path.join(LOG_FOLDER, self.log_name)
        self.config(self.log_file, file_level, size, count)

    def config(self, log_file, file_level, size, count):
        """set config for logger"""
        self.logger.setLevel(MAPPING[file_level])
        self.fh = handlers.RotatingFileHandler(log_file, mode='a+',
                                               maxBytes=size, backupCount=count, encoding='utf-8')
        self.fh.setLevel(MAPPING[file_level])


        formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s", datefmt=DATEFMT)

        self.fh.setFormatter(formatter)

        self.logger.addHandler(self.fh)

    def debug(self, msg):
        if msg is not None:
            self.logger.debug(msg)

    def info(self, msg):
        if msg is not None:
            self.logger.info(msg)

    def warning(self, msg):
        if msg is not None:
            self.logger.warning(msg)

    def error(self, msg):
        if msg is not None:
            self.logger.error(msg)

    def critical(self, msg):
        if msg is not None:
            self.logger.critical(msg)

    def traceback(self):
        """Log exception traceback to logger"""
        import sys
        import traceback
        info = sys.exc_info()
        lines = traceback.format_exception(info[0], info[1], info[2])
        for line in lines:
            elines = line.splitlines()
            for eline in elines:
                self.logger.critical(eline.strip())
