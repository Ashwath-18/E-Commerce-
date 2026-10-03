# Cartify Setup

## Step 1

Install dependencies

```bash
pip install -r requirements.txt
```

## Step 2

Start MongoDB

## Step 3

Initialize the database (run from the project root, only the first time)

```bash
python -m database.initialize_database
```

## Step 4 (optional)

For the AI assistant, create a `.env` file in the project root:

```
AI_API_KEY=your_key_here
AI_MODEL=your_model_name
```

## Step 5

Run the application

```bash
python app.py
```

Default login: `admin` / `admin`