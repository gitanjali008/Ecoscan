# Project Brief: EcoScan (Reewild Full Stack Take-Home)

## Goal
A web app that scans photos of clothing, estimates each item's carbon footprint,
awards eco-reward points for eco-savings, and shows offers the user can redeem.
Assessed on backend + frontend skill, product design and technical vision.

## User story
1. User uploads a photo of clothing (file upload OR camera capture).
2. App identifies the clothing items in the image.
3. App estimates a carbon footprint for each item.
4. App shows the total carbon score and eco-reward points based on eco-savings.
5. App shows offers the user can redeem with their points.

## Frontend requirements
- Clean, user-friendly UI to upload or capture a picture.
- Show identified items, each item's carbon footprint, and total eco-reward points.
- Show offers the user can redeem with their points.
- Stack: React (our choice: React + Vite).

## Backend requirements
- Image analysis endpoint: accepts an image, recognises clothing items,
  returns items with estimated carbon scores.
- Eco-score calculation: carbon footprint per item + eco-reward points.
- Offers retrieval: offers the user can redeem, based on points.
- Carbon assumptions per item type (e.g. T-shirt = 5 kg CO2, Jeans = 10 kg CO2),
  stored in an in-memory dictionary.
- Image recognition: OpenAI GPT-4 vision, an open-source model, or a mock.
- Stack: Python FastAPI (our choice).

## Technical requirements
- No database; in-memory storage only.
- Basic unit tests for core functionality.
- Error handling for common cases (e.g. invalid image upload).
- Code structure must allow easy updates to carbon data and future
  integration with accurate external data sources.

## Documentation (README.md)
- Setup: install dependencies, configure env variables, start the app.
- Run: local URLs for frontend and backend.
- How to run tests.
- Carbon footprint assumptions explained.
- Code structure and design decisions.
- Deployment link, if deployed.
- Enhancement proposals, split into Product Improvements and Technical Scaling:
  - Scaling the backend for larger user loads (caching, database, etc.).
  - A better carbon model (materials, brand data, garment condition).
  - UX insights (e.g. sustainability comparisons).
  - Integration with external APIs for real-time carbon data.

## Submission
- Public GitHub repo with all code, tests and docs.
- Small, frequent commits so reviewers can follow the thinking.
- Optional: deploy (Vercel / Render / Azure) and record a demo video (Loom).

## Evaluation criteria
- Functionality: upload, item recognition and eco-score calculation work.
- Code quality: clean, modular, well structured.
- Documentation: detailed, easy to follow.
- User experience: intuitive and polished UI.
- Scalability and product vision: realistic, valuable enhancements.