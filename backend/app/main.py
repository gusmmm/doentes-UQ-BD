from fastapi import FastAPI
from .routes.patient import patient

app = FastAPI()
app.include_router(patient, prefix="/patient", tags=["patient"])

### notes
# check the video https://www.youtube.com/watch?v=G7hZlOLhhMY
