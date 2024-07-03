import sys
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QSizePolicy, QVBoxLayout, QHeaderView, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QStackedWidget, QInputDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Function to fetch nutrition data from Edamam API
def fetch_nutrition_data(ingredient, app_id, app_key):
    url = f'https://api.edamam.com/api/nutrition-data?app_id={app_id}&app_key={app_key}&ingr={ingredient}'
    response = requests.get(url)
    data = response.json()
    return data

# Function to calculate nutrition for a recipe
def calculate_nutrition(recipe, app_id, app_key):
    total_nutrition = {}
    for ingredient, quantity in recipe.items():
        data = fetch_nutrition_data(f"{quantity} {ingredient}", app_id, app_key)
        if 'totalNutrients' in data:
            for nutrient, value in data['totalNutrients'].items():
                if nutrient not in total_nutrition:
                    total_nutrition[nutrient] = {'quantity': 0, 'unit': value.get('unit', '')}
                total_nutrition[nutrient]['quantity'] += value.get('quantity', 0)
    return total_nutrition

# Function to get ingredients and quantities from user
def get_recipe_from_user():
    recipe = {}
    while True:
        ingredient, ok = QInputDialog.getText(None, 'Enter Ingredient', 'Enter ingredient (or type "done" to finish):')
        if not ok or ingredient.lower() == 'done':
            break
        quantity, ok = QInputDialog.getText(None, 'Enter Quantity', f'Enter quantity of {ingredient}:')
        if not ok:
            break
        recipe[ingredient] = quantity
    return recipe

# Map nutrient keys to their full names
NUTRIENT_NAMES = {
    'ENERC_KCAL': 'Calories',
    'FAT': 'Total Fat',
    'FASAT': 'Saturated Fat',
    'FAMS': 'Monounsaturated Fat',
    'FAPU': 'Polyunsaturated Fat',
    'CHOCDF': 'Total Carbohydrates',
    'FIBTG': 'Dietary Fiber',
    'SUGAR': 'Sugars',
    'PROCNT': 'Protein',
    'CHOLE': 'Cholesterol',
    'NA': 'Sodium',
    'CA': 'Calcium',
    'MG': 'Magnesium',
    'K': 'Potassium',
    'FE': 'Iron',
    'ZN': 'Zinc',
    'P': 'Phosphorus',
    'VITA_RAE': 'Vitamin A',
    'VITC': 'Vitamin C',
    'THIA': 'Thiamin (Vitamin B1)',
    'RIBF': 'Riboflavin (Vitamin B2)',
    'NIA': 'Niacin (Vitamin B3)',
    'VITB6A': 'Vitamin B6',
    'FOLDFE': 'Folate (Vitamin B9)',
    'TOCPHA': 'Vitamin E',
    'VITK1': 'Vitamin K',
    'WATER': 'Water'
}

class IngredientHistoryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.history_label = QLabel('Ingredient History:')
        self.history_label.setStyleSheet("font-size: 16px; color: purple;")
        layout.addWidget(self.history_label)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(2)
        self.history_table.setHorizontalHeaderLabels(["Ingredient Name", "Quantity"])
        layout.addWidget(self.history_table)
        self.setLayout(layout)
        
        # Set table column resizing policy to stretch
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_ingredient(self, ingredient, quantity):
        row_position = self.history_table.rowCount()
        self.history_table.insertRow(row_position)
        self.history_table.setItem(row_position, 0, QTableWidgetItem(ingredient))
        self.history_table.setItem(row_position, 1, QTableWidgetItem(quantity))

from PyQt5.QtGui import QFont

class WelcomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Create and style the label
        label = QLabel("Welcome to Nutrition Calculator!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 50px; color: black; font-family: Cheri Liney;")

        # Set the font for the button
        font = QFont("Cheri Liney", 20)
        
        # Create and style the button
        button = QPushButton("Let's Calculate")
        button.setFont(font)
        button.setStyleSheet("background-color: lightgreen;")
        button.clicked.connect(self.go_to_main_page)

        # Add label and button to the layout
        layout.addWidget(label)
        layout.addWidget(button)

        self.setLayout(layout)

    def go_to_main_page(self):
        self.parent().setCurrentIndex(1)

class MainPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.ingredients_label = QLabel('Enter Ingredient:')
        self.ingredients_label.setStyleSheet("font-size: 16px; color: purple;")
        self.layout.addWidget(self.ingredients_label)
        self.ingredients_input = QLineEdit()
        self.layout.addWidget(self.ingredients_input)
        self.quantity_label = QLabel('Enter Quantity:')
        self.quantity_label.setStyleSheet("font-size: 16px; color: purple;")
        self.layout.addWidget(self.quantity_label)
        self.quantity_input = QLineEdit()
        self.layout.addWidget(self.quantity_input)
        self.add_button = QPushButton('Add Ingredient')
        self.add_button.setStyleSheet("font-size: 16px; background-color: lightblue;")
        self.add_button.clicked.connect(self.add_ingredient)
        self.layout.addWidget(self.add_button)
        self.calculate_button = QPushButton('Calculate Nutrition')
        self.calculate_button.setStyleSheet("font-size: 16px; background-color: lightgreen;")
        self.calculate_button.clicked.connect(self.calculate_nutrition)
        self.layout.addWidget(self.calculate_button)
        self.ingredient_history_widget = IngredientHistoryWidget()
        self.layout.addWidget(self.ingredient_history_widget)
        self.setLayout(self.layout)

    def add_ingredient(self):
        ingredient = self.ingredients_input.text().strip()
        quantity = self.quantity_input.text().strip()
        if ingredient and quantity:
            self.ingredients_input.clear()
            self.quantity_input.clear()
            self.parent.recipe[ingredient] = quantity
            self.ingredient_history_widget.add_ingredient(ingredient, quantity)

    def calculate_nutrition(self):
        self.parent.calculate_nutrition()

class ResultPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Create and style the result label
        self.result_label = QLabel('Total Nutrition per Serving:')
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("font-size: 24px; color: green; font-family: Helvetica; font-weight: bold;")
        layout.addWidget(self.result_label)
        
        # Create and style the result text
        self.result_text = QTextEdit()
        self.result_text.setStyleSheet("font-family: Helvetica; font-size: 18px;")
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        # Set the table alignment to center
        self.result_text.setAlignment(Qt.AlignCenter)
        
        self.setLayout(layout)

    def set_result_text(self, total_nutrition, recipe):
        text = '<b>Input Foods:</b><br><br>'
        for ingredient, quantity in recipe.items():
            text += f"{ingredient}: {quantity}<br>"
        text += '<br><b>Total Nutrition per Serving:</b><br><br>'
        text += '<table border="1" cellpadding="5">'
        for nutrient, value in total_nutrition.items():
            if nutrient in NUTRIENT_NAMES:
                text += f"<tr><td>{NUTRIENT_NAMES[nutrient]}</td><td>{value['quantity']:.2f} {value['unit']}</td></tr>"
        text += '</table>'
        self.result_text.setHtml(text)

class NutritionCalculatorApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.recipe = {}
        self.addWidget(WelcomePage(self))
        self.addWidget(MainPage(self))
        self.result_page = ResultPage(self)
        self.addWidget(self.result_page)
        self.setWindowTitle('Nutrition Calculator')
        self.setStyleSheet("background-color: pink;")

    def calculate_nutrition(self):
        app_id = '1234' #numerical value
        app_key = 'xxxx' #alphaumerical value
        total_nutrition = calculate_nutrition(self.recipe, app_id, app_key)
        self.result_page.set_result_text(total_nutrition, self.recipe)
        self.setCurrentIndex(2)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = NutritionCalculatorApp()
    window.show()
    sys.exit(app.exec_())


