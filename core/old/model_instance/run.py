import uvicorn




if __name__ == "__main__":
    uvicorn.run(
        "web:app", 
        host="127.0.0.1", 
        port=int(8999), 
        reload=False, 
        log_level="warning"
        )