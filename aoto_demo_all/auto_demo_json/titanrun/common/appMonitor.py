# -*- coding: utf-8 -*-
import argparse
import commands
import datetime
import multiprocessing
import os
import re
import sys
import time
from threading import Timer
import traceback
import matplotlib
from adbtool import AdbTools
matplotlib.use('Agg', warn=True)
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

DATA_TITLE = "时间,应用占用CPU,总占用CPU,总内存(MB),Native(MB),Dalvik(MB),电量,流量(Kb/s),上行,下行,线程数,FPS\n"
HEAP_PROFILE = True
AndroidVersion = 0
argvmap = {}


class BaseProfiler():
    def __init__(self, adb):
        self.adb = adb
        self.androidversion = self.adb.get_device_sdk_version()


class CpuProfiler(BaseProfiler):
    def __init__(self, pid, adb):
        BaseProfiler.__init__(self, adb)
        self.appPid = pid
        self.processcpuRatioList = []
        self.cpuRatioList = []
        self.lastRecord = {}
        self.lastTime = 0
        self.titile = ["应用占用CPU(%)", "总占用CPU(%)"]

    def init(self):
        processCpu = self.getprocessCpuStat()
        idleCpu, totalCpu = self.getTotalCpuStat()
        self.lastRecord["processCpu"] = processCpu
        self.lastRecord["idleCpu"] = idleCpu
        self.lastRecord["totalCpu"] = totalCpu
        self.lastTime = datetime.datetime.now()

    '''
    参考：
    http://blog.sina.com.cn/s/blog_aed19c1f0102wcun.html
    http://www.blogjava.net/fjzag/articles/317773.html
    '''

    def getprocessCpuStat(self):
        stringBuffer = self.adb.adb('shell "cat /proc/%s/stat"'%self.appPid).read().decode(
            "utf-8").strip()
        r = re.compile("\\s+")
        toks = r.split(stringBuffer)
        processCpu = float(long(toks[13]) + long(toks[14]))
        return processCpu

    def getTotalCpuStat(self):
        child_out = self.adb.adb('shell "cat /proc/stat"').read().decode("utf-8").strip().split("\r\r\n")[
            0]
        if int(self.androidversion) >= 19:
            child_out = self.adb.adb('shell "cat /proc/stat |grep ^cpu\ "').read().decode(
                "utf-8").strip()
            if " grep: not found" in child_out:
                child_out = \
                    self.adb.adb('shell "cat /proc/stat"').read().decode("utf-8").strip().split("\r\r\n")[0]
        r = re.compile(r'(?<!cpu)\d+')
        toks = r.findall(child_out)
        idleCpu = float(toks[3])
        totalCpu = float(reduce(lambda x, y: long(x) + long(y), toks))
        return idleCpu, totalCpu

    def profile(self):
        processCpu = self.getprocessCpuStat()
        idleCpu, totalCpu = self.getTotalCpuStat()
        currentTime = datetime.datetime.now()
        diffTime = currentTime - self.lastTime
        retry = False
        processcpuRatio = 100 * (processCpu - self.lastRecord["processCpu"]) / (totalCpu - self.lastRecord["totalCpu"])
        cpuRatio = 100 * ((totalCpu - idleCpu) - (self.lastRecord["totalCpu"] - self.lastRecord["idleCpu"])) / (
            totalCpu - self.lastRecord["totalCpu"])
        if (diffTime.seconds * 1000 + diffTime.microseconds / 1000) < abs(totalCpu - self.lastRecord["totalCpu"]):
            print("cpu data abnormal, do again!")
            retry = True

        self.lastTime = currentTime
        self.lastRecord["processCpu"] = processCpu
        self.lastRecord["idleCpu"] = idleCpu
        self.lastRecord["totalCpu"] = totalCpu

        # 保存画图数据
        self.processcpuRatioList.append(round(float(processcpuRatio), 2))
        self.cpuRatioList.append(round(float(cpuRatio), 2))

        return round(float(processcpuRatio), 2), round(float(cpuRatio), 2), retry


class ThreadCount(BaseProfiler):
    def __init__(self, pid, appName, adb):
        BaseProfiler.__init__(self, adb)
        self.appPid = pid
        self.appName = appName
        self.title = ["线程数"]
        self.threadcount = []

    def getThreadCount(self):
        sendCmd = self.adb.adb('shell "top -d 2 -n 1 |grep %s"' % self.appPid) \
            .read().decode("utf-8").strip()
        if self.appName not in sendCmd:
            return 0
        items = filter(lambda x: x != '', sendCmd.split(' '))
        # Android 7.0 以上top： PID USER     PR  NI CPU% S  #THR     VSS     RSS PCY Name
        # Android 7.0 以下top:  PID PR CPU% S  #THR     VSS     RSS PCY UID      Name
        threadcount = 0
        if items and len(items) > 4:
            if int(self.androidversion) < 24:
                threadcount = items[4]
            else:  # 7.0 以上
                threadcount = items[6]
            self.threadcount.append(threadcount)
            return threadcount
        else:
            print("Error passing thread count with pid %s" % self.appPid)
        return 0


class MemProfiler(BaseProfiler):
    def __init__(self, pid, adb):
        BaseProfiler.__init__(self, adb)
        self.appPid = pid
        self.adb = adb
        self.PSSList = []
        self.NativeHeapList = []
        self.DalvikHeapList = []
        self.lastRecord = {}
        self.titile = ["总内存(MB)", "NativeHeap(MB)", "DalvikHeap(MB)"]

    def timeout(self, p):
        if p.poll() is None:
            print('appmonitor Error: process taking too long to complete--terminating')
            p.kill()

    def getProcessMem(self):
        if HEAP_PROFILE == False:
            return 0, 0, 0

        cmdProcess = self.adb.adb('shell "dumpsys meminfo {}"'.format(self.appPid))
        output = ""
        my_timer = Timer(30, self.timeout, [cmdProcess])
        try:
            my_timer.start()
            output = cmdProcess.read().decode("utf-8").strip()
        except ValueError as err:
            print(err.args)
        finally:
            my_timer.cancel()

        m = re.search(r'TOTAL\s*(\d+)', output)
        native = r'Native Heap\s*(\d+)'
        dalvik = r'Dalvik Heap\s*(\d+)'
        if int(self.androidversion) < 19:
            native = r'Native \s*(\d+)'
            dalvik = r'Dalvik \s*(\d+)'
        m1 = re.search(native, output)
        m2 = re.search(dalvik, output)
        PSS = float(m.group(1))
        NativeHeap = float(m1.group(1))
        DalvikHeap = float(m2.group(1))
        return PSS, NativeHeap, DalvikHeap

    def profile(self):
        PSS, NativeHeap, DalvikHeap = self.getProcessMem()

        self.PSSList.append(round(PSS / 1024, 2))
        self.NativeHeapList.append(round(NativeHeap / 1024, 2))
        self.DalvikHeapList.append(round(DalvikHeap / 1024, 2))

        return round(PSS / 1024, 2), round(NativeHeap / 1024, 2), round(DalvikHeap / 1024, 2)


class powerProfiler(BaseProfiler):
    def __init__(self, adb):
        BaseProfiler.__init__(self, adb)
        self.adb = adb
        self.PowList = []
        self.lastRecord = {}
        self.titile = ["电量"]

    def timeout(self, p):
        if p.poll() is None:
            print('appmonitor Error: process taking too long to complete--terminating')
            p.kill()

    def getProcesspow(self):
        if HEAP_PROFILE == False:
            return 0, 0, 0

        cmdProcess = self.adb.adb('shell "dumpsys battery |grep level"')
        output = ""
        my_timer = Timer(30, self.timeout, [cmdProcess])
        try:
            my_timer.start()
            output = cmdProcess.read().decode("utf-8").strip()
        except ValueError as err:
            print(err.args)
        finally:
            my_timer.cancel()

        battery = output.split(':')[1]
        return battery

    def profile(self):
        battery = self.getProcesspow()

        self.PowList.append(battery)

        return battery


class FlowProfiler():
    def __init__(self, pid, adb):
        self.appPid = pid
        self.adb = adb
        self.flowList = []
        self.lastRecord = {}
        self.lastTime = 0
        self.titile = ["流量(Kb/s)", "上行流量(Kb/s)", "下行流量(Kb/s)"]

    def init(self):
        sendNum, recNum = self.getFlow()
        self.lastRecord["sendNum"] = sendNum
        self.lastRecord["recNum"] = recNum
        self.lastTime = datetime.datetime.now()

    def getFlow(self):
        output = self.adb.adb('shell "cat /proc/{}/net/dev|grep wlan0"'.format(self.appPid)).read()
        m = re.search(r'wlan0:\s*(\d+)\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*\d+\s*(\d+)', output)
        if m:
            recNum = float(m.group(1))
            sendNum = float(m.group(2))
        else:
            print("Couldn't get rx and tx data from: %s!" % output)
            recNum = 0.0
            sendNum = 0.0
        return sendNum, recNum

    def profile(self):
        sendNum, recNum = self.getFlow()
        currentTime = datetime.datetime.now()
        diffTime = currentTime - self.lastTime

        seconds = diffTime.seconds + float(diffTime.microseconds) / 1000000
        flow = (((sendNum - self.lastRecord["sendNum"]) + (recNum - self.lastRecord["recNum"])) / 1024) / seconds
        flow = round(flow, 2)
        upflow = (sendNum - self.lastRecord["sendNum"]) / 1024 / seconds
        downflow = (recNum - self.lastRecord["recNum"]) / 1024 / seconds
        upflow = round(upflow, 2)
        downflow = round(downflow, 2)

        self.lastTime = currentTime
        self.lastRecord["sendNum"] = sendNum
        self.lastRecord["recNum"] = recNum

        if flow > 0:
            self.flowList.append(flow)
        return flow, upflow, downflow


class GpuProfiler():
    gpuReachable = True

    def __init__(self, pid, adb):
        self.appPid = pid
        self.adb = adb
        self.titile = ["GPU(%)"]

    def getGpuInfo(self):
        # cmd = "adb -s %s shell cat /sys/class/kgsl/kgsl-3d0/gpubusy" % self.adb.device_serial()
        # pipe = os.popen(cmd)
        # text = pipe.read()
        # sts = pipe.close()
        # if sts is None: sts = 0
        load = -0.0
        if not self.gpuReachable:
            return load
        text = self.adb.adb('shell "cat /sys/class/kgsl/kgsl-3d0/gpubusy"').read().decode("utf-8").strip()
        # 某些手机没有权限,如三星s7edge金色
        if text == '':
            # 进一步确认
            status, output = commands.getstatusoutput(
                'adb -s %s shell cat /sys/class/kgsl/kgsl-3d0/gpubusy' % self.adb.get_devices()[0])
            if status == 256:
                self.gpuReachable = False
                return load
        if text[-1:] == '\n':  text = text[:-1]
        if "No such file or directory" in text or "Permission denied" in text:
            self.gpuReachable = False
            return load
        # return sts, text
        m = re.search(r'\s*(\d+)\s*(\d+)', text)
        if m:
            utilization_arg_1 = m.group(1)
            utilization_arg_2 = m.group(2)
        else:
            # print "Couldn't get utilization data from: %s!" % text
            self.gpuReachable = False
            return load
        if float(utilization_arg_2) != 0:
            load = str(round((float(utilization_arg_1) / float(utilization_arg_2)) * 100, 2))
        return load


class AppTrafficProfiler():
    def __init__(self, pid, adb):
        self.appPid = pid
        self.adb = adb
        self.flowList = []
        self.lastRecord = {}
        self.lastTime = 0
        self.uid = 0
        self.networktype = 'wlan0'
        self.titile = ["流量(Kb/s)", "上行流量(Kb/s)", "下行流量(Kb/s)"]

    def init(self):
        self.uid = self.getuid()
        self.lastRecord["recNum"], self.lastRecord["sendNum"] = self.getTrafficData()
        self.lastTime = datetime.datetime.now()

    def getuid(self):
        uid = 0
        uids = self.adb.adb('shell "cat /proc/%s/status |grep Uid"'%self.appPid).read().decode("utf-8").strip()
        if uids:
            uid = uids.split('\t')[1]
        return uid

    # http://www.voidcn.com/article/p-tolukrhb-vz.html
    # http://www.dreamingfish123.info/?p=1154
    def getTrafficData(self):
        if not self.uid:
            return 0, 0
        # /proc/net/xt_qtaguid/stats各列代表意义
        # idx iface acct_tag_hex uid_tag_int cnt_set rx_bytes rx_packets tx_bytes tx_packets
        # rx_tcp_bytes rx_tcp_packets rx_udp_bytes rx_udp_packets rx_other_bytes rx_other_packets
        # tx_tcp_bytes tx_tcp_packets tx_udp_bytes tx_udp_packets tx_other_bytes tx_other_packets
        # iface：网络性质［wlan0－wifi流量 lo－本地流量 rmnet0－3g/2g流量 ...］
        output = self.adb.adb('shell "cat /proc/net/xt_qtaguid/stats |grep %s |grep %s"'%(self.uid, self.networktype)).read().decode("utf-8").strip()
        rx_list = []
        tx_list = []
        totalrx = 0.0
        totaltx = 0.0
        if output:
            lines = output.splitlines()
            validlines = filter(lambda x: len(x) > 1, lines)
            for item in validlines:
                # 前后台流量都算上
                if len(item.strip().split()) < 8:  # 保证第6／8项存在
                    print(r'wrong format in data: split len='
                                    + str(len(item.split())) + r'content: ' + str(item))
                    continue
                rx_bytes = item.split()[5]
                tx_bytes = item.split()[7]
                rx_list.append(int(rx_bytes))
                tx_list.append(int(tx_bytes))
            totalrx = float(sum(rx_list))
            totaltx = float(sum(tx_list))
        else:
            # 无效或没有使用网络
            print(
                "Couldn't get rx and tx data from: /proc/net/xt_qtaguid/stats! maybe this uid doesnot connetc to net")
        return totalrx, totaltx

    def profile(self):
        recNum, sendNum = self.getTrafficData()
        currentTime = datetime.datetime.now()
        diffTime = currentTime - self.lastTime

        seconds = diffTime.seconds + float(diffTime.microseconds) / 1000000
        upflow = (sendNum - self.lastRecord["sendNum"]) / 1024 / seconds
        downflow = (recNum - self.lastRecord["recNum"]) / 1024 / seconds
        upflow = round(upflow, 2) if sendNum > 0 else -0.0
        downflow = round(downflow, 2) if recNum > 0 else -0.0
        flow = round(upflow + downflow, 2)

        self.lastTime = currentTime
        self.lastRecord["sendNum"] = sendNum
        self.lastRecord["recNum"] = recNum

        if flow > 0:
            self.flowList.append(flow)
        return flow, upflow, downflow


class fpsProfiler():
    def __init__(self, adb, appName):
        self.adb = adb
        self.appName = appName
        self.titile = ["Fps"]

    def get_fps(self):
        cmd = " shell dumpsys gfxinfo %s" % self.appName
        results = self.adb.adb(cmd).read().decode("utf-8").strip()
        frames = [x for x in results.split('\n')]
        frame_count = len(frames)
        jank_count = 0
        vsync_overtime = 0
        render_time = 0
        for frame in frames:
            time_block = re.split(r'\s+', frame.strip())
            if len(time_block) == 3:
                try:
                    render_time = float(time_block[0]) + float(time_block[1]) + float(time_block[2])
                except Exception as e:
                    render_time = 0

            '''
            当渲染时间大于16.67，按照垂直同步机制，该帧就已经渲染超时
            那么，如果它正好是16.67的整数倍，比如66.68，则它花费了4个垂直同步脉冲，减去本身需要一个，则超时3个
            如果它不是16.67的整数倍，比如67，那么它花费的垂直同步脉冲应向上取整，即5个，减去本身需要一个，即超时4个，可直接算向下取整
            最后的计算方法思路：
            执行一次命令，总共收集到了m帧（理想情况下m=128），但是这m帧里面有些帧渲染超过了16.67毫秒，算一次jank，一旦jank，
            需要用掉额外的垂直同步脉冲。其他的就算没有超过16.67，也按一个脉冲时间来算（理想情况下，一个脉冲就可以渲染完一帧）
            所以FPS的算法可以变为：
            m / （m + 额外的垂直同步脉冲） * 60
            '''
            if render_time > 16.67:
                jank_count += 1
                if render_time % 16.67 == 0:
                    vsync_overtime += int(render_time / 16.67) - 1
                else:
                    vsync_overtime += int(render_time / 16.67)

        fps = int(frame_count * 60 / (frame_count + vsync_overtime))
        return fps


class app_monitor(multiprocessing.Process):
    timeout_in_seconds = 120

    def __init__(self, period, fileName, appName, serial=None, image=False, duration=0):
        multiprocessing.Process.__init__(self)
        self.adb = AdbTools(device_id=serial)

        self.appPid = 0
        self.appName = appName
        self.period = period
        self.fileName = fileName + ".csv"
        self.pigName = fileName + ".png"
        # self.getappPid()
        self.running = True
        self.lastRecord = {}
        self.image = image
        self.duration = duration

    # self.is_alive = False
    def stop(self):
        self.running = False
        # try:
        #     while self.running and self.getAppPid() == self.appPid and self.getAppPid() != 0:
        #         print("appmonitor process still alive, wait ...")
        #         time.sleep(1)
        # except:
        #     pass

    def getAppPid(self):
        outputs = self.adb.adb('shell "top -n 1"').read().decode("utf-8").strip()
        m = None
        for i in range(0, 3):
            if i == 0:
                pkg = self.appName
            else:
                pkg = '.'.join(self.appName.split('.')[:-i])
            r = "(\d+).*\s+%s" % pkg
            m = re.search(r, outputs)
            if m:
                break
        if m:
            return m.group(1)
        else:
            print("app still not get up")
            return 0

    def waitForAppReady(self):
        start_time = time.time()
        while self.appPid == 0:
            elapsed = time.time() - start_time
            # 做完一部分任务后,判断是否超时
            if elapsed >= app_monitor.timeout_in_seconds:
                print("获取app pid超时，退出")
                self.running = False
                break

            print("appPid == 0")
            self.appPid = self.getAppPid()

    def pic(self, processcpuRatioList, cpuRatioList, PSSList, NativeHeapList, DalvikHeapList, flowList):
        # matplotlib.use('Agg')
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
        # 设置右侧Y轴显示百分数
        fmt = '%.2f%%'
        yticks = mtick.FormatStrFormatter(fmt)

        def minY(listData):
            return round(min(listData) * 0.8, 2)

        def maxY(listData):
            return round(max(listData) * 1.2, 2)

        def drawSubplot(pos, x, y, xlabels, ylabels):
            plt.subplot(pos)
            plt.plot(x, y, label=ylabels)
            plt.xlabel(xlabels)
            plt.ylabel(ylabels)
            plt.ylim(minY(y), maxY(y))
            # plt.title(u'应用CPU')
            plt.legend()

        plt.figure(figsize=(20, 10))
        import platform
        systemtype = platform.system()
        winFlag = False
        if 'Darwin' in systemtype or 'Linux' in systemtype:
            xcoordinate = 'time(s)'
        elif 'Windows' in systemtype:
            xcoordinate = u'时间(秒)'
            winFlag = True
        else:
            # 默认
            xcoordinate = 'time(s)'

        timeList = [x * 2 for x in range(len(processcpuRatioList))]
        drawSubplot(321, timeList, processcpuRatioList, xcoordinate, u'应用CPU(%)' if winFlag else 'app-cpu(%)')
        plt.gca().yaxis.set_major_formatter(yticks)

        timeList = [x * 2 for x in range(len(cpuRatioList))]
        drawSubplot(322, timeList, cpuRatioList, xcoordinate, u"总cpu(%)" if winFlag else 'cpu(%)')
        plt.gca().yaxis.set_major_formatter(yticks)

        timeList = [x * 2 for x in range(len(PSSList))]
        drawSubplot(323, timeList, PSSList, xcoordinate, u"总内存(MB)" if winFlag else 'PSS(M)')

        timeList = [x * 2 for x in range(len(NativeHeapList))]
        drawSubplot(324, timeList, NativeHeapList, xcoordinate, u"Native内存(MB)" if winFlag else 'Native(M)')

        timeList = [x * 2 for x in range(len(DalvikHeapList))]
        drawSubplot(325, timeList, DalvikHeapList, xcoordinate, u"Dalvik内存(MB)" if winFlag else 'Dalvik(M)')

        timeList = [x * 2 for x in range(len(flowList))]
        drawSubplot(326, timeList, flowList, xcoordinate, u"流量(kb/s)" if winFlag else 'Traffic(Kbps)')

        # plt.gca().yaxis.set_minor_formatter(yticks)
        plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.55, wspace=0.25)

        # plt.show()
        print self.pigName
        plt.savefig(self.pigName)

    def run(self):
        # 根据应用的包名称 获取CPU以及内存占用
        print("app_monitor run \n")
        # self.is_alive = True

        # 等待获取到被监控app的pid后才开始采集数据
        print "waitForAppReady begin"
        self.waitForAppReady()
        print "Tracing pid = ", self.appPid
        print "waitForAppReady end\n"

        flowProfile = FlowProfiler(self.appPid, self.adb)
        cpuProfile = CpuProfiler(self.appPid, self.adb)
        memProfile = MemProfiler(self.appPid, self.adb)
        # gpuProfile = GpuProfiler(self.appPid, self.adb)
        powProfiler = powerProfiler(self.adb)
        threadcountProfile = ThreadCount(self.appPid, self.appName, self.adb)
        fpsprofiler = fpsProfiler(self.adb,self.appName)

        flowProfile.init()
        cpuProfile.init()

        trafficProfile = AppTrafficProfiler(self.appPid, self.adb)
        trafficProfile.init()

        if os.path.exists(self.fileName):
            os.remove(self.fileName)

        with open(self.fileName, "w+") as f:
            # f.write('\xEF\xBB\xBF')
            f.write(DATA_TITLE)

            firstRun = True
            errorTimes = 0
            print DATA_TITLE.replace(",", "     ").decode("utf-8")
            starttime = datetime.datetime.now()

            while self.running:
                try:
                    nowtime = datetime.datetime.now()
                    if self.duration != 0 and ((nowtime - starttime).total_seconds() - self.period - 1) >= self.duration:
                        self.running = False
                        break
                    str_now_time = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(time.time()))
                    processcpuRatio, cpuRatio, retry = cpuProfile.profile()
                    if retry:
                        time.sleep(float(self.period))
                        continue
                    PSS, NativeHeap, DalvikHeap = memProfile.profile()
                    # flow, upflow, downflow = flowProfile.profile()
                    flow, upflow, downflow = trafficProfile.profile()
                    # gpu = gpuProfile.getGpuInfo()
                    battery = powProfiler.profile()
                    fps = fpsprofiler.get_fps()
                    threadcount = threadcountProfile.getThreadCount()

                    write_str = "%s,%5s,%5s,%6s,%6s,%6s,%s,%6s,%6s,%6s,%5s,%s" % (
                        str(str_now_time), str(processcpuRatio), str(cpuRatio), str(PSS), str(NativeHeap), str(DalvikHeap),
                        str(battery), str(flow), str(upflow), str(downflow), str(threadcount), str(fps))

                    print write_str.replace(",", "     ")
                    # 将数据写入文件
                    f.write(write_str + "\n")
                    f.flush()

                except Exception, e:
                    traceback.print_exc()
                    self.appPid = 0
                    self.waitForAppReady()
                    print "Tracing pid = ", self.appPid
                    print "waitForAppReady end\n"

                # 中低端机型采集数据命令需要约3秒，高端机型如P9／小米6等采集命令时间较短
                collectiontime = (datetime.datetime.now() - nowtime).total_seconds()
                if float(self.period) > float(collectiontime):
                    time.sleep(float(self.period - collectiontime))

        if self.image:
            print u"开始绘图了"
            self.pic(cpuProfile.processcpuRatioList, cpuProfile.cpuRatioList, memProfile.PSSList,
                     memProfile.NativeHeapList,
                     memProfile.DalvikHeapList, trafficProfile.flowList)
            print u"绘图结束了"

        self.running = False


# def help_notice():
# 	print u"用法 python appMonitor.py 2 d:\ com.yy.me device2342"
# 	print u"参数：[时间间隔] [结果存放目录] [包名] [设备ID](只连一台手机不需要此参数)"
# 	sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help=u'verbose')
    parser.add_argument('-t', '--time', type=int, default=2, help=u'interval time in second. 时间间隔（秒）')
    parser.add_argument('-d', '--duration', type=int, default=0, help=u'duration in second. 持续时间（秒）')
    parser.add_argument('-s', '--device', help=u'target device serial. 设备ID')
    parser.add_argument('-f', '--file', help=u'the path to store the result file, no ext. 结果存放文件,不带扩展名')
    parser.add_argument('-p', '--package', default='com.duowan.mobile', help=u'target app package name. 包名')
    parser.add_argument('-i', '--image', default=False, help=u'to draw results or not. 是否画图，默认不画')
    args = parser.parse_args()

    adbInstance = AdbTools()
    if adbInstance and (len(adbInstance.get_devices()) == 0
                        or len(adbInstance.get_devices()) > 1) and not args.device:
        print 'no device or multiple devices attached but no one is specified.'
        print adbInstance.get_devices()
        raise RuntimeError

    # 默认值
    argvmap['timeIntervalSec'] = args.time
    argvmap['result'] = os.path.abspath(args.file) if args.file \
        else os.path.join(os.getcwd(), datetime.datetime.now().strftime("%Y%m%d_%H-%M-%S"))
    argvmap['package'] = args.package
    argvmap['serial'] = args.device if args.device else adbInstance.get_devices()[0]
    argvmap['image'] = args.image
    argvmap['duration'] = args.duration

    for key in argvmap.keys():
        print key, ': ', argvmap[key]

    # period, fileName, appName, serial，
    appMonitor = app_monitor(argvmap['timeIntervalSec'], argvmap['result'], argvmap['package'],
                             argvmap['serial'], argvmap['image'],
                             argvmap['duration'])

    appMonitor.start()

# print u"休眠60"
# time.sleep(60)
#
# print "stop"
# appMonitor.terminate()
