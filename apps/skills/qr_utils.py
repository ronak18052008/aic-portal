import qrcode
import io
import base64

def generate_qr_code_data_uri(content: str) -> str:
    """
    Generates a QR code for the given content string and returns it
    as a base64-encoded PNG Data URI suitable for HTML <img> tags.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(content)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1e1b4b", back_color="#ffffff")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"
