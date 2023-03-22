"""
The final version of Recivery APP

"""


from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import time

from foodcom import FoodCom
from googlemap import GoogleMap
from foodkeeper import FoodKeeper


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QtCore.QRect(60, 120, 500, 61))
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(120, 450, 371, 61))
        self.lineEdit.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lineEdit.setAutoFillBackground(False)
        self.lineEdit.setObjectName("lineEdit")
        # self.lineEdit.setStyleSheet(u"background-color:rgb(214, 255, 188);")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 593, 24))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.FoodCom = None
        self.GoogleMap = None
        self.FoodKeeper = None

        self.foodcom_recommand_mode = False
        self.first_recommand = True

        self.foodcom_search_mode = False
        self.keywords = None
        self.first_search = True

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def food_recommend(self, rank_page_no=None):
        return self.FoodCom.rank_page(rank_page_no)

    def food_search(self, keywords=None):
        return self.FoodCom.search(keywords)

    def food_keep_advise(self, keywords):
        return self.FoodKeeper.food_keep_advise(keywords)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Recivery"))
        self.label.setText(_translate(
            "MainWindow", u"Do you want to access the app online or offline? ON/OFF", None))
        self.lineEdit.setText(_translate("MainWindow", ""))
        self.lineEdit.returnPressed.connect((self.lineedit1))

    # Set online/offline mode
    def lineedit1(self):
        if self.lineEdit.text().lower() == 'on':
            self.FoodCom = FoodCom(True)
            self.GoogleMap = GoogleMap(True)
            self.FoodKeeper = FoodKeeper(True)
        else:
            self.FoodCom = FoodCom(False)
            self.GoogleMap = GoogleMap(False)
            self.FoodKeeper = FoodKeeper(False)

        self.label.setText(
            u"Do you want to search for a specific dish or our recommended dishes？S/R")
        self.lineEdit.returnPressed.disconnect((self.lineedit1))
        self.lineEdit.setText("")
        self.lineEdit.returnPressed.connect((self.lineedit2))

    # Recommend dish
    def lineedit2(self):
        if self.lineEdit.text().lower() == 'r' or (self.lineEdit.text().lower() == 'y' and self.foodcom_recommand_mode):
            self.foodcom_recommand_mode = True
            self.foodcom_search_mode = False

            self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
            self.scrollArea.setGeometry(QtCore.QRect(120, 200-20, 400, 225+20))
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOn)
            self.scrollArea.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOn)
            self.scrollArea.setWidgetResizable(False)
            self.scrollArea.setObjectName("scrollArea")
            self.scrollAreaWidgetContents = QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(
                QtCore.QRect(0, 0, 500, 600))
            self.scrollAreaWidgetContents.setObjectName(
                "scrollAreaWidgetContents")
            self.label2 = QLabel(self.scrollAreaWidgetContents)
            self.label2.setGeometry(QtCore.QRect(10, 10, 3000, 3000))
            self.label2.setAlignment(
                QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.label2.setObjectName("label2")
            self.scrollArea.show()
            self.label2.show()
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)

            # recommend intro
            intro_success = False
            while not intro_success:
                if self.first_recommand:
                    recommendation_dic, display = self.food_recommend(1)
                    self.first_recommand = False
                else:
                    recommendation_dic, display = self.food_recommend()
                print(display)
                self.label2.setText(display)
                self.label2.show()
                self.lineEdit.setText("")

                # bad network
                if not recommendation_dic["available"]:
                    print("Retry in 10 seconds\nCheck you Internet status please")
                    time.sleep(10)
                else:
                    intro_success = True

            self.label.setText(
                u"\nDo you want to see other recommendation? Y/N: ")

            self.lineEdit.returnPressed.disconnect((self.lineedit2))
            self.lineEdit.setText("")
            self.lineEdit.returnPressed.connect((self.lineedit2))

        elif self.lineEdit.text().lower() == 's':
            self.label.setText(u"Please input any dish you want to search: ")
            self.lineEdit.returnPressed.disconnect((self.lineedit2))
            self.lineEdit.setText("")
            self.lineEdit.returnPressed.connect((self.lineedit3))

        else:
            self.label.setText(
                u"Choose the recipe you want to see detail？Only Number: ")
            self.lineEdit.returnPressed.disconnect((self.lineedit2))
            self.lineEdit.setText("")
            self.lineEdit.returnPressed.connect((self.lineedit4))

    # Search dish
    def lineedit3(self):
        if not self.lineEdit.text().lower() == 'n':
            if self.keywords == None:
                self.keywords = self.lineEdit.text().lower()

            if not self.first_search:
                self.label2.setText("")

            self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
            self.scrollArea.setGeometry(QtCore.QRect(120, 200-20, 400, 225+20))
            self.scrollArea.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOn)
            self.scrollArea.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarAlwaysOn)
            self.scrollArea.setWidgetResizable(False)
            self.scrollArea.setObjectName("scrollArea")
            self.scrollAreaWidgetContents = QtWidgets.QWidget()
            self.scrollAreaWidgetContents.setGeometry(
                QtCore.QRect(0, 0, 500, 600))
            self.scrollAreaWidgetContents.setObjectName(
                "scrollAreaWidgetContents")
            self.label2 = QLabel(self.scrollAreaWidgetContents)
            self.label2.setGeometry(QtCore.QRect(10, 10, 3000, 3000))
            self.label2.setAlignment(
                QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.label2.setObjectName("label2")
            self.scrollArea.show()
            self.label2.show()
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)

            # search intro
            intro_success = False
            while not intro_success:
                if self.first_search:
                    search_dic, display = self.food_search(self.keywords)
                    self.first_search = False
                else:
                    search_dic, display = self.food_search()
                print(display)

                self.label2.setText("")
                self.label2.setText(display)
                self.label2.show()
                self.lineEdit.setText("")

                # bad network
                if not search_dic["available"]:
                    print("Retry in 10 seconds\nCheck you Internet status please")
                    time.sleep(10)
                    continue
                # meaningless input, 0 search result
                if len(search_dic["recipes"]) == 0:
                    keywords = input(
                        "\nPlease input any dish you want to search: ")
                else:
                    intro_success = True

            self.label.setText(
                u"Do you want to see next page? Y/N:              ")
            self.lineEdit.returnPressed.disconnect((self.lineedit3))
            self.lineEdit.setText("")
            self.lineEdit.returnPressed.connect((self.lineedit3))

        else:
            self.label.setText(
                u"Choose the recipe you want to see detail？Only Number: ")
            self.lineEdit.returnPressed.disconnect((self.lineedit3))
            self.lineEdit.setText("")
            self.lineEdit.returnPressed.connect((self.lineedit4))

    # Display recipe detail
    def lineedit4(self):
        dish_id = self.lineEdit.text().lower()
        dish_id = str(dish_id)

        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(120, 200-20, 400, 225+20))
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(False)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(
            QtCore.QRect(0, 0, 1500, 2000))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.label2 = QLabel(self.scrollAreaWidgetContents)
        self.label2.setGeometry(QtCore.QRect(10, 10, 3000, 3000))
        self.label2.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.label2.setObjectName("label2")
        self.scrollArea.show()
        self.label2.show()
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        detail_suc = False
        while not detail_suc:
            detail_dic, display = self.FoodCom.one_recipe_detail(dish_id)
            print(display)

            self.label2.setText("")
            self.label2.setText(display)
            self.label2.show()
            self.lineEdit.setText("")

            # unknown id
            if not detail_dic["legal"]:
                dish_id = input(
                    "\nChoose the recipe you want to see detail？Only Number: ")
                dish_id = str(dish_id)
                continue
            # sucess
            if detail_dic["recipe_available"]:
                detail_suc = True
            # bad network
            else:
                print("Retry in 10 seconds\nCheck you Internet status please")
                time.sleep(10)

        self.label.setText(
            u"Do you want to buy the ingredients and try it? Y/N: ")
        self.lineEdit.returnPressed.disconnect((self.lineedit4))
        self.lineEdit.setText("")
        self.lineEdit.returnPressed.connect((self.lineedit5))

    # Buy ingredient
    def lineedit5(self):
        self.label2.setText("")
        if self.lineEdit.text().lower() == 'y':

            self.label.setText(
                u"Please input your address so that we can recommend the best grocery stores: ")
            self.lineEdit.returnPressed.disconnect((self.lineedit5))
            self.lineEdit.setText("")
            self.lineEdit.returnPressed.connect((self.lineedit6))
        else:
            self.label.setText(
                u"Do you want to know how to keep the ingredients? Y/N: ")
            self.label2.setText("")
            self.lineEdit.returnPressed.disconnect((self.lineedit5))
            self.lineEdit.setText("")
            self.lineEdit.returnPressed.connect((self.lineedit7))

    # Recommand grocery store
    def lineedit6(self):
        address = self.lineEdit.text().lower()
        self.label2.setText("")

        self.GoogleMap.generate_form(address)
        grocery_dic = self.GoogleMap.info()

        self.generate_table()
        row, vol = len(grocery_dic), 4
        self.tableWidget.setColumnCount(vol)
        self.tableWidget.setRowCount(row)
        a = 0

        for i in ['index', 'grocery store',  'rating', 'distance <']:
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(a, item)
            item = self.tableWidget.horizontalHeaderItem(a)
            item.setText(i)
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignBottom)
            a = a + 1

        list_rows = []
        for index, row_ in grocery_dic.iterrows():
            list_rows.append([index, row_['grocery store'], row_[
                             'rating'], row_['distance <']])

        try:
            for i in range(row):
                for j in range(vol):
                    self.Table_Data(i, j, list_rows[i][j])
            # self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeColumnToContents(1)
            self.tableWidget.show()
        except Exception as e:
            print(e)

        self.label2.setText("")
        self.lineEdit.setText("")

        self.GoogleMap.plot_pie()
        self.GoogleMap.plot_bar()

        self.label.setText(
            u"Choose the grocery stores you want to see detail？Only Numbers (divide with ,) : ")
        self.lineEdit.returnPressed.disconnect((self.lineedit6))
        self.lineEdit.setText("")
        self.lineEdit.returnPressed.connect((self.lineedit9))

    # Recommand grocery store
    def lineedit9(self):
        grocery_id = self.lineEdit.text().split(',')
        rows = []
        for id in grocery_id:
            rows.append(eval(id))
        grocery_detail = self.GoogleMap.details(rows)
        print(grocery_detail)

        # Get the number of records, used to set the number of rows in the table
        row, vol = len(grocery_detail), 7
        self.tableWidget.setColumnCount(vol)
        self.tableWidget.setRowCount(row)
        a = 0

        # Set TableWidget header information
        for i in ['index', 'grocery store',  'rating', 'distance <', 'rating_numbers', 'opening_now', 'location']:
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(a, item)
            item = self.tableWidget.horizontalHeaderItem(a)
            item.setText(i)
            item.setTextAlignment(QtCore.Qt.AlignHCenter |
                                  QtCore.Qt.AlignBottom)
            a = a + 1

        list_rows = []
        for index, row_ in grocery_detail.iterrows():
            list_rows.append([index, row_['grocery store'], row_['rating'], row_[
                             'distance <'], row_['rating_numbers'], row_['opening_now'], row_['location']])

        try:
            for i in range(row):
                for j in range(vol):
                    self.Table_Data(i, j, list_rows[i][j])
            self.tableWidget.resizeColumnToContents(1)
            self.tableWidget.show()

        except Exception as e:
            print(e)

        self.label2.setText("")
        self.lineEdit.setText("")

        self.label.setText(
            u"Do you want to know how to keep the ingredients? Y/N: ")
        self.label2.setText("")
        self.lineEdit.returnPressed.disconnect((self.lineedit9))
        self.lineEdit.setText("")
        self.lineEdit.returnPressed.connect((self.lineedit7))

    # Display ingredients
    def lineedit7(self):
        self.tableWidget.deleteLater()
        if self.lineEdit.text().lower() == 'y':
            self.label2.setText("")
            self.scrollAreaWidgetContents.setGeometry(
                QtCore.QRect(0, 0, 600, 1000))  # scroll box size setting
            self.label2.setText(self.FoodCom.display_ingredients())
            self.label2.show()
            self.lineEdit.setText("")

            self.label.setText(
                u"Choose the ingredients for keep advice? Only Numbers (divide with ,) : ")
            self.lineEdit.returnPressed.disconnect((self.lineedit7))
            self.lineEdit.setText("")
            self.lineEdit.returnPressed.connect((self.lineedit8))

    # Display food keep advise
    def lineedit8(self):
        ingredients_id = self.lineEdit.text().split(',')
        ingredients = []
        for id in ingredients_id:
            ingredients.append(self.FoodCom.ingredients[eval(id)])

        keep_dict = self.food_keep_advise(ingredients)
        advise = ""
        for food, head in keep_dict.items():
            print('For freshness and quality, {} should be consumed within:'.format(food))
            advise = advise + \
                'For freshness and quality,  {} should be consumed within:'.format(
                    food)
            advise = advise + "\n"
            try:
                if 'Pantry_Metric' in head.keys():
                    advise = advise + '{} - {} {} if in the pantry from the date of purchase\n'.format(head['Pantry_Min'],
                                                                                                       head['Pantry_Max'],
                                                                                                       head['Pantry_Metric'])

                    print('{} - {} {} if in the pantry from the date of purchase'
                          .format(head['Pantry_Min'], head['Pantry_Max'], head['Pantry_Metric']))
                if 'DOP_Pantry_Metric' in head.keys():
                    advise = advise + '{} - {} {} if pantry stored after opening\n'.format(head['DOP_Pantry_Min'],
                                                                                           head['DOP_Pantry_Max'],
                                                                                           head['DOP_Pantry_Metric'])
                    print('{} - {} {} if pantry stored after opening'
                          .format(head['DOP_Pantry_Min'], head['DOP_Pantry_Max'], head['DOP_Pantry_Metric']))
                if 'DOP_Refrigerate_Metric' in head.keys():
                    advise = advise + '{} - {} {} if refrigerated from the date of purchase\n'.format(
                        head['DOP_Refrigerate_Min'], head['DOP_Refrigerate_Max'], head['DOP_Refrigerate_Metric'])
                    print('{} - {} {} if refrigerated from the date of purchase'
                          .format(head['DOP_Refrigerate_Min'], head['DOP_Refrigerate_Max'], head['DOP_Refrigerate_Metric']))
                if 'DOP_Freeze_Metric' in head.keys():
                    advise = advise + '{} - {} {} if pantry stored after opening\n'.format(head['DOP_Freeze_Min'],
                                                                                           head['DOP_Freeze_Max'],
                                                                                           head['DOP_Freeze_Metric'])
                    print('{} - {} {} if pantry stored after opening\n'
                          .format(head['DOP_Freeze_Min'], head['DOP_Freeze_Max'], head['DOP_Freeze_Metric']))
                print('\n')

            except:
                print('Sorry, no more food keep advice for this ingredient')
                advise = advise + "Sorry, no more food keep advice for this ingredient\n"
            print('\n')
            advise = advise + "\n"
            advise = advise + "\n"

            self.scrollAreaWidgetContents.setGeometry(
                QtCore.QRect(0, 0, 600, 1000))  # scroll box size setting

            self.label2.setText("")
            self.label2.setText(advise)
            self.label2.show()
            self.lineEdit.setText("")

    def generate_table(self):
        try:
            self.tableWidget.deleteLater()
        except:
            pass
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(120, 200-20, 400, 225+20))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(True)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget.setStyleSheet("background-color:white}")
        self.tableWidget.horizontalHeader().setStyleSheet(
            "QHeaderView::section{font:12pt ; color: black;height:40px; font-weight: bold;};")

    def Table_Data(self, i, j, data):
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setItem(i, j, item)
        item = self.tableWidget.item(i, j)
        item.setText(str(data))
        item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main = QMainWindow()
    main_ui = Ui_MainWindow()
    main_ui.setupUi(main)

    main.show()
    sys.exit(app.exec_())
