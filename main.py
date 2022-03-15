from flask import Flask, request
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("YOUR_MONGODB_CLIENT_LINK")
db = cluster["bakery"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("message")
    number = request.form.get("sender")
    res = {"reply": ""}
    user = users.find_one({"number": number})
    if bool(user) == False:
        res["reply"] += '\n' + ("Hi, thanks for contacting *The Red Velvet*.\nYou can choose from one of the options below: "
                    "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                    "To get our *address*")
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res["reply"] += '\n' + ("Please enter a valid response")
            return str(res)

        if option == 1:
            res["reply"] += '\n' + (
                "You can contact us through phone or e-mail.\n\n*Phone*: +62-xxxx-xxxx \n*E-mail* : redvelvet@gmail.com")
        elif option == 2:
            res["reply"] += '\n' + ("You have entered *ordering mode*.")
            users.update_one(
                {"number": number}, {"$set": {"status": "ordering"}})
            res["reply"] += '\n' + (
                "You can select one of the following cakes to order: \n\n1️⃣ Red Velvet  \n2️⃣ Dark Forest \n3️⃣ Ice Cream Cake"
                "\n4️⃣ Plum Cake \n5️⃣ Sponge Cake \n6️⃣ Genoise Cake \n7️⃣ Angel Cake \n8️⃣ Carrot Cake \n9️⃣ Fruit Cake  \n0️⃣ Go Back")
        elif option == 3:
            res["reply"] += '\n' + ("We work from *9 a.m. to 5 p.m*.")
        elif option == 4:
            res["reply"] += '\n' + (
                "We have multiple stores across the city. Our main center is at Cibiru, Bandung*")
        else:
            res["reply"] += '\n' + ("Please enter a valid response")
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res["reply"] += '\n' + ("Please enter a valid response")
            return str(res)
        print(option)
        if option == 0:
            users.update_one(
                {"number": number}, {"$set": {"status": "main"}})
            res["reply"] += '\n' + ("You can choose from one of the options below: "
                        "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                        "To get our *address*")
        elif 1 <= option <= 9:
            cakes = ["Red Velvet Cake", "Dark Forest Cake", "Ice Cream Cake",
                     "Plum Cake", "Sponge Cake", "Genoise Cake", "Angel Cake", "Carrot Cake", "Fruit Cake"]
            selected = cakes[option - 1]
            users.update_one(
                {"number": number}, {"$set": {"status": "address"}})
            users.update_one(
                {"number": number}, {"$set": {"item": selected}})
            res["reply"] += '\n' + ("Excellent choice 😉")
            res["reply"] += '\n' + ("Please enter your address to confirm the order")
        else:
            res["reply"] += '\n' + ("Please enter a valid response")
    elif user["status"] == "address":
        selected = user["item"]
        res["reply"] += "\n" +  "Thanks for shopping with us 😊"
        res["reply"] += "\n" +  f"Your order for *{selected}* has been received and will be delivered within an hour"
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one(
            {"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res["reply"] += "\n" +  ("Hi, thanks for contacting again.\nYou can choose from one of the options below: "
                     "\n\n*Type*\n\n 1️⃣ To *contact* us \n 2️⃣ To *order* snacks \n 3️⃣ To know our *working hours* \n 4️⃣ "
                     "To get our *address*")
        users.update_one(
            {"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
    return str(res)


if __name__ == "__main__":
    app.run(port=5000)
