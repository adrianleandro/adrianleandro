import logging
import os
import httpx

class OCRService:
    def __init__(self):
        # Use the same base URL as wine recommendations but with /ocr endpoint
        base_url = os.getenv('RECOMMENDATIONS_API_URL')
        self.ocr_url = f"{base_url}/ocr"
        logging.info(f"OCR Service initialized with URL: {self.ocr_url}")
    
    async def extract_menu_text(self, image_path: str) -> str:
        """
        Extract text from menu image using external OCR API
        
        Args:
            image_path: Path to the image file on disk
            
        Returns:
            Extracted text from the menu image
        """
        try:
            # Read the image file
            with open(image_path, 'rb') as img_file:
                # OCR endpoint expects 'image' as the file field name
                files = {'image': (image_path.split('/')[-1], img_file, 'image/jpeg')}
                
                # Make request to OCR endpoint
                async with httpx.AsyncClient(timeout=60.0) as client:
                    logging.info(f"Sending image to OCR endpoint: {self.ocr_url}")
                    response = await client.post(
                        self.ocr_url,
                        files=files
                    )
                    response.raise_for_status()
                    
                    # Extract text from response
                    result = response.json()
                    extracted_text = result.get('text', '')
                    
                    if not extracted_text:
                        logging.warning("OCR returned empty text")
                        raise ValueError("No text extracted from image")
                    
                    return extracted_text
                    
        except httpx.HTTPError as e:
            logging.error(f"HTTP error during OCR extraction: {str(e)}")
            raise Exception(f"Failed to connect to OCR service: {str(e)}")
        except FileNotFoundError:
            logging.error(f"Image file not found: {image_path}")
            raise Exception(f"Image file not found: {image_path}")
        except Exception as e:
            logging.error(f"OCR extraction failed: {str(e)}")
            raise Exception(f"OCR extraction failed: {str(e)}")