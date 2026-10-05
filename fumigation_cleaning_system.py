import json
import os
from datetime import datetime

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "service_records.txt")
customers, bookings, receipts = [], [], []
ADMIN_PASSWORD = "Admin123"

services = {
    "S001": ("Laundry", "Pickup", 15000, "Basket"),
    "S002": ("Small Carpet Cleaning", "Pickup", 55000, "Carpet"),
    "S003": ("Big Carpet Cleaning", "Pickup", 85000, "Carpet"),
    "S004": ("1 Sofa Cleaning", "On-Site", 100000, "Service"),
    "S005": ("2 Sofas Cleaning", "On-Site", 150000, "Service"),
    "S006": ("3 Sofa Set Cleaning", "On-Site", 250000, "Service"),
    "S007": ("House Cleaning 2-3 Rooms", "On-Site", 300000, "Service"),
    "S008": ("House Cleaning 4+ Rooms", "On-Site", 500000, "Service"),
    "S009": ("Office Cleaning", "On-Site", 600000, "Service"),
    "S010": ("Fumigation", "On-Site", 550000, "Service"),
    "S011": ("Deep Cleaning", "On-Site", 1300000, "Service"),
    "S012": ("Curtain Cleaning", "Pickup", 50000, "Pair"),
    "S013": ("Outdoor - Compound Pavers", "On-Site", 1000000, "Service"),
    "S014": ("Outdoor - Roofing Tiles", "On-Site", 2000000, "Service"),
    "S015": ("Outdoor - Slashing", "On-Site", 300000, "Yard"),
    "S016": ("Outdoor - Rocks Cleaning", "On-Site", 800000, "Service")
}

pickup_stages = ["Booking Confirmed", "Pickup Scheduled", "Picked Up",
                 "Service In Progress", "Ready for Delivery", "Completed"]

onsite_stages = ["Booking Confirmed", "Team Assigned", "Team Dispatched",
                 "Service In Progress", "Completed"]

def save():
    with open(FILE, "w") as f:
        json.dump({"customers": customers, "bookings": bookings,
                   "receipts": receipts}, f, indent=4)

def load():
    global customers, bookings, receipts
    try:
        with open(FILE, "r") as f:
            data = json.load(f)
            customers = data.get("customers", [])
            bookings = data.get("bookings", [])
            receipts = data.get("receipts", [])
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def new_id(records, prefix, field):
    numbers = []
    for record in records:
        try:
            numbers.append(int(record[field][1:]))
        except:
            pass
    return prefix + str(max(numbers, default=0) + 1).zfill(3)

def positive_number(message):
    while True:
        try:
            value = int(input(message))
            if value > 0:
                return value
        except ValueError:
            pass
        print("Enter a valid number greater than zero.")

def view_services():
    print("\nAVAILABLE SERVICES")
    print("-" * 75)
    for code, (name, category, price, unit) in services.items():
        cost = f"UGX {price:,}"
        if unit != "Service":
            cost += f" per {unit.lower()}"
        print(f"{code:<6}{name:<42}{cost}")

def register():
    print("\nCUSTOMER REGISTRATION")
    name = input("Full name: ").strip()
    phone = input("Phone: ").strip()
    email = input("Email: ").strip().lower()

    if not name or not phone or not email:
        print("All fields are required.")
        return

    if (not email.endswith("@gmail.com") or email == "@gmail.com"
            or email.count("@") != 1 or " " in email):
        print("Enter a valid Gmail address ending with @gmail.com.")
        return

    if any(c["phone"] == phone for c in customers):
        print("Phone number already registered.")
        return

    customer = {
        "customer_id": new_id(customers, "C", "customer_id"),
        "name": name,
        "phone": phone,
        "email": email
    }

    customers.append(customer)
    save()
    print("Registered successfully.")
    print("Customer ID:", customer["customer_id"])

def find_customer():
    value = input("Customer ID or phone: ").strip().lower()
    for customer in customers:
        if customer["customer_id"].lower() == value or customer["phone"] == value:
            return customer
    print("Customer not found.")
    return None

def quantity(name):
    if name == "Laundry":
        return positive_number("Number of baskets: ")
    if "Carpet" in name:
        return positive_number("Number of carpets: ")
    if name == "Curtain Cleaning":
        return positive_number("Number of curtain pairs: ")
    if name == "Outdoor - Slashing":
        return positive_number("Number of yards: ")
    return 1

def select_services(multiple=False):
    items = []

    while True:
        view_services()
        code = input("\nService ID: ").strip().upper()

        if code not in services:
            print("Invalid Service ID.")
            continue

        if any(item["code"] == code for item in items):
            print("Service already selected.")
            continue

        name, category, price, unit = services[code]
        qty = quantity(name)

        items.append({
            "code": code,
            "name": name,
            "category": category,
            "quantity": qty,
            "subtotal": price * qty,
            "discount": 0
        })

        if not multiple:
            break

        if input("Add another service? Y/N: ").strip().upper() != "Y":
            break

    return items

def apply_discounts(items):
    carpet_quantity = sum(item["quantity"] for item in items
                          if "Carpet" in item["name"])

    outdoor_total = sum(item["subtotal"] for item in items
                        if item["name"].startswith("Outdoor"))

    for item in items:
        qualifies = (
            (item["name"] == "Laundry" and item["quantity"] >= 3)
            or ("Carpet" in item["name"] and carpet_quantity >= 3)
            or (item["name"].startswith("Outdoor")
                and outdoor_total > 500000)
        )

        if qualifies:
            item["discount"] = item["subtotal"] * 0.05

        item["total"] = item["subtotal"] - item["discount"]

def make_booking(customer, multiple=False):
    items = select_services(multiple)

    if not items:
        return

    apply_discounts(items)

    original = sum(i["subtotal"] for i in items)
    discount = sum(i["discount"] for i in items)
    total = sum(i["total"] for i in items)

    pickup_total = sum(i["total"] for i in items
                       if i["category"] == "Pickup")

    onsite_total = sum(i["total"] for i in items
                       if i["category"] == "On-Site")

    required = pickup_total * 0.50 + onsite_total * 0.40

    if pickup_total and onsite_total:
        category = "Mixed"
    elif pickup_total:
        category = "Pickup"
    else:
        category = "On-Site"

    address = input("Service/Pickup address: ").strip()
    date = input("Service date DD/MM/YYYY: ").strip()

    if not address or not date:
        print("Address and date are required.")
        return

    booking = {
        "booking_id": new_id(bookings, "B", "booking_id"),
        "customer_id": customer["customer_id"],
        "customer_name": customer["name"],
        "items": items,
        "category": category,
        "original_cost": original,
        "discount": discount,
        "final_cost": total,
        "required_payment": required,
        "amount_paid": 0,
        "balance": total,
        "payment_status": "Unpaid",
        "address": address,
        "service_date": date,
        "pickup_status": "Pending Payment" if pickup_total else None,
        "onsite_status": "Pending Payment" if onsite_total else None,
        "rating": 0,
        "comment": ""
    }

    bookings.append(booking)
    save()

    print("\nBOOKING CREATED")
    print("Booking ID:", booking["booking_id"])

    for item in items:
        print(f"{item['name']} x {item['quantity']} "
              f"- UGX {item['total']:,.0f}")

    print(f"Original Cost: UGX {original:,.0f}")
    print(f"Discount: UGX {discount:,.0f}")
    print(f"Final Cost: UGX {total:,.0f}")
    print(f"Initial Payment Required: UGX {required:,.0f}")

    if category == "Pickup":
        print("Payment Rule: 50% before pickup.")
    elif category == "On-Site":
        print("Payment Rule: 40% before service.")
    else:
        print("Payment Rule: 50% for pickup services "
              "and 40% for on-site services.")

def mine(customer):
    return [b for b in bookings
            if b["customer_id"] == customer["customer_id"]]

def find_booking(records):
    if not records:
        print("No bookings found.")
        return None

    code = input("Booking ID: ").strip().upper()

    for booking in records:
        if booking["booking_id"] == code:
            return booking

    print("Booking not found.")
    return None

def show_booking(booking):
    print("\nBooking:", booking["booking_id"])
    print("Customer:", booking["customer_name"])

    for item in booking["items"]:
        print("-", item["name"], "x", item["quantity"])

    print("Date:", booking["service_date"])
    print("Address:", booking["address"])

    if booking.get("pickup_status"):
        print("Pickup Status:", booking["pickup_status"])

    if booking.get("onsite_status"):
        print("On-Site Status:", booking["onsite_status"])

    print("Payment:", booking["payment_status"])
    print(f"Total: UGX {booking['final_cost']:,.0f}")
    print(f"Paid: UGX {booking['amount_paid']:,.0f}")
    print(f"Balance: UGX {booking['balance']:,.0f}")

def view_bookings(customer):
    records = mine(customer)

    if not records:
        print("No bookings found.")
        return

    for booking in records:
        show_booking(booking)

def progress(title, current, stages):
    print("\n" + title)

    if current == "Pending Payment":
        print("[►] Pending Payment")

        for stage in stages:
            print("[ ]", stage)

        return

    try:
        position = stages.index(current)

        for index, stage in enumerate(stages):
            if index < position:
                symbol = "[✓]"
            elif index == position:
                symbol = "[►]"
            else:
                symbol = "[ ]"

            print(symbol, stage)

    except ValueError:
        print("Current Stage:", current)

def track(customer):
    booking = find_booking(mine(customer))

    if not booking:
        return

    print("\nBOOKING TRACKING")
    print("Booking:", booking["booking_id"])
    print("Date:", booking["service_date"])
    print("Payment:", booking["payment_status"])

    if booking.get("pickup_status"):
        progress("PICKUP SERVICES",
                 booking["pickup_status"], pickup_stages)

    if booking.get("onsite_status"):
        progress("ON-SITE SERVICES",
                 booking["onsite_status"], onsite_stages)

def payment(customer):
    booking = find_booking(mine(customer))

    if not booking:
        return

    if booking["balance"] == 0:
        print("Booking already fully paid.")
        return

    needed = max(
        booking["required_payment"] - booking["amount_paid"],
        0
    )

    print(f"Balance: UGX {booking['balance']:,.0f}")

    if needed:
        print(f"Amount needed to confirm: UGX {needed:,.0f}")

    while True:
        try:
            amount = float(
                input("Enter payment without commas: UGX ")
            )

            if 0 < amount <= booking["balance"]:
                break

        except ValueError:
            pass

        print("Invalid payment amount.")

    booking["amount_paid"] += amount
    booking["balance"] -= amount

    booking["payment_status"] = (
        "Fully Paid"
        if booking["balance"] == 0
        else "Partially Paid"
    )

    if booking["amount_paid"] >= booking["required_payment"]:

        if booking.get("pickup_status") == "Pending Payment":
            booking["pickup_status"] = "Booking Confirmed"

        if booking.get("onsite_status") == "Pending Payment":
            booking["onsite_status"] = "Booking Confirmed"

    receipt = {
        "receipt_id": new_id(receipts, "R", "receipt_id"),
        "booking_id": booking["booking_id"],
        "customer_id": customer["customer_id"],
        "customer_name": customer["name"],
        "payment": amount,
        "paid": booking["amount_paid"],
        "balance": booking["balance"],
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    }

    receipts.append(receipt)
    save()
    show_receipt(receipt)

def show_receipt(receipt):
    print("\nDIGITAL RECEIPT")
    print("Receipt:", receipt["receipt_id"])
    print("Booking:", receipt["booking_id"])
    print("Customer:", receipt["customer_name"])
    print("Date:", receipt["date"])
    print(f"Payment: UGX {receipt['payment']:,.0f}")
    print(f"Total Paid: UGX {receipt['paid']:,.0f}")
    print(f"Balance: UGX {receipt['balance']:,.0f}")

def view_receipts(customer):
    records = [r for r in receipts
               if r["customer_id"] == customer["customer_id"]]

    if not records:
        print("No receipts found.")
        return

    for receipt in records:
        show_receipt(receipt)

def finished(booking):
    pickup_done = booking.get(
        "pickup_status"
    ) in [None, "Completed"]

    onsite_done = booking.get(
        "onsite_status"
    ) in [None, "Completed"]

    return pickup_done and onsite_done

def rate(customer):
    records = [
        b for b in mine(customer)
        if finished(b) and b["rating"] == 0
    ]

    if not records:
        print("No completed booking available for rating.")
        return

    booking = find_booking(records)

    if not booking:
        return

    while True:
        rating = positive_number("Rating 1-5: ")

        if rating <= 5:
            break

        print("Maximum rating is 5.")

    booking["rating"] = rating
    booking["comment"] = input("Comment: ").strip()

    save()
    print("Feedback submitted.")

def update_stage(booking, service_type):
    pickup = service_type == "Pickup"

    field = "pickup_status" if pickup else "onsite_status"
    stages = pickup_stages if pickup else onsite_stages

    if booking.get(field) == "Pending Payment":
        print("Initial payment must be made first.")
        return

    for number, stage in enumerate(stages, 1):
        print(number, "-", stage)

    try:
        choice = int(input("Select status: "))

        if 1 <= choice <= len(stages):
            booking[field] = stages[choice - 1]
            save()
            print("Status updated.")
        else:
            print("Invalid choice.")

    except ValueError:
        print("Invalid choice.")

def update_status():
    booking = find_booking(bookings)

    if not booking:
        return

    if booking["amount_paid"] < booking["required_payment"]:
        print("Required initial payment has not been made.")
        return

    if booking["category"] == "Pickup":
        update_stage(booking, "Pickup")

    elif booking["category"] == "On-Site":
        update_stage(booking, "On-Site")

    else:
        print("1. Update Pickup Services")
        print("2. Update On-Site Services")

        choice = input("Choice: ")

        if choice == "1":
            update_stage(booking, "Pickup")
        elif choice == "2":
            update_stage(booking, "On-Site")
        else:
            print("Invalid choice.")

def feedback():
    records = [b for b in bookings if b["rating"] > 0]

    if not records:
        print("No feedback available.")
        return

    for booking in records:
        print("\nBooking:", booking["booking_id"])
        print("Customer:", booking["customer_name"])
        print("Rating:", booking["rating"], "/5")
        print("Comment:", booking["comment"])

def customer_account(customer):
    while True:
        print("\nCUSTOMER ACCOUNT")
        print("1. View Services")
        print("2. Book One Service")
        print("3. Book Multiple Services")
        print("4. View My Bookings")
        print("5. Track Booking")
        print("6. Make Payment")
        print("7. View Receipts")
        print("8. Rate Completed Service")
        print("9. Logout")

        choice = input("Choice: ")

        if choice == "1":
            view_services()
        elif choice == "2":
            make_booking(customer)
        elif choice == "3":
            make_booking(customer, True)
        elif choice == "4":
            view_bookings(customer)
        elif choice == "5":
            track(customer)
        elif choice == "6":
            payment(customer)
        elif choice == "7":
            view_receipts(customer)
        elif choice == "8":
            rate(customer)
        elif choice == "9":
            break
        else:
            print("Invalid choice.")

def customer_menu():
    while True:
        print("\nCUSTOMER MENU")
        print("1. Register")
        print("2. Access Account")
        print("3. View Services")
        print("4. Back")

        choice = input("Choice: ")

        if choice == "1":
            register()

        elif choice == "2":
            customer = find_customer()

            if customer:
                customer_account(customer)

        elif choice == "3":
            view_services()

        elif choice == "4":
            break

        else:
            print("Invalid choice.")

def admin_login():
    attempts = 0

    while attempts < 4:
        password = input("Admin Password: ")

        if password == ADMIN_PASSWORD:
            print("Admin access granted.")
            return True

        attempts += 1

        if attempts < 4:
            print("Incorrect password.")
            print("Attempts used:", attempts)
            print("Attempts remaining:", 4 - attempts)

        else:
            print("Fourth incorrect password.")
            print("System closing for security.")
            return False

def admin_menu():
    while True:
        print("\nADMIN / STAFF")
        print("1. View All Bookings")
        print("2. Search Booking")
        print("3. Update Booking Status")
        print("4. View Feedback")
        print("5. Back")

        choice = input("Choice: ")

        if choice == "1":
            if bookings:
                for booking in bookings:
                    show_booking(booking)
            else:
                print("No bookings.")

        elif choice == "2":
            booking = find_booking(bookings)

            if booking:
                show_booking(booking)

        elif choice == "3":
            update_status()

        elif choice == "4":
            feedback()

        elif choice == "5":
            break

        else:
            print("Invalid choice.")

def main():
    load()

    while True:
        print("\nFUMIGATION AND CLEANING SERVICE SYSTEM")
        print("1. Customer")
        print("2. Administrator / Staff")
        print("3. Exit")

        choice = input("Choice: ")

        if choice == "1":
            customer_menu()

        elif choice == "2":
            if admin_login():
                admin_menu()
            else:
                save()
                print("Program closed safely.")
                break

        elif choice == "3":
            save()
            print("Program closed safely.")
            break

        else:
            print("Invalid choice.")

main()