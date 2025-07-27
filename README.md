# 🛒 SupplySync

SupplySync is a web-based **street food supply chain management system** built using **Flask**, **MongoDB**, and **Twilio**. The platform connects **vendors** (street food sellers) with **suppliers** (raw material providers), enabling seamless material requests, order tracking, and status updates.

---

## Features

## Multi-User Roles
- **Vendor**
  - Register and login with OTP verification
  - Browse available suppliers and raw materials
  - Place and view material orders
  - Track order status (Pending, Confirmed, Shipped, Delivered)

- **Supplier**
  - Register and login with OTP verification
  - View incoming orders from vendors
  - Update order status dynamically

---

## Tech Stack

`| Layer      | Technology               |
|------------|--------------------------|
| Backend    | Flask (Python)           |
| Frontend   | HTML, CSS, JavaScript    |
| Database   | MongoDB (PyMongo)        |
| OTP Service| Twilio                   |
| Templating | Jinja2                   |`

---

## 📁 Directory Structure

`SupplySync/
├── app.py
├── templates/
│ ├── signup.html
│ ├── login.html
│ ├── vendor_orders.html
│ ├── supplier_orders.html
│ └── ...
├── uploads/
│ └── images
├── requirements.txt
└── README.md`


## OTP Verification

- Uses **Firebase Authentication** to send OTP to the user's phone during signup/login.
- Verifies entered OTP before allowing access.
- For Testing: Use phone number - 9876543210 and OTP - 123456


## Order Status Workflow

1. Vendor places an order → Status: `Pending`
2. Supplier reviews and updates to:
   - `Confirmed`
   - `Shipped`
   - `Delivered`

## Future Enhancements
Admin panel for system monitoring

Chat between vendor and supplier

Email notifications

Dashboard analytics (charts, graphs)

Responsive UI improvements

# License
This project is licensed under the MIT License — feel free to use and modify.
