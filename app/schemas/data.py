from app.schemas.tracker import CourierPartnerName


TableNames = {
    CourierPartnerName.DELHIVERY: "delhivery_tracker_data",
    CourierPartnerName.DTDC: "dtdc_tracker_data",
    CourierPartnerName.SHIPROCKET: "shiprocket_tracker_data",
}

PincodeSKUTable = "pincode_sku"

DatabaseName = "tracker_db"
