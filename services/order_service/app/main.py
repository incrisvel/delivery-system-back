import os
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
from services.order_service.app.core.db.session import engine
from services.order_service.app.core.db.base import Base
from services.order_service.app.modules.dish.router import router as dishes
from services.order_service.app.modules.delivery.router import router as deliveries
from services.order_service.app.modules.order.router import router as orders
from services.order_service.app.modules.establishment.router import (
    router as establishments,
)
from services.order_service.app.core.messaging import container as rabbitmq_container
from services.order_service.app.core.websocket import container as ws_container
from fastapi.middleware.cors import CORSMiddleware

from services.order_service.app.core.cluster.ring import (
    RingNode
)


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dishes)
app.include_router(deliveries)
app.include_router(orders)
app.include_router(establishments)


PORT = int(os.getenv("PORT", 8000))
ring = RingNode(my_address=f"http://127.0.0.1:{PORT}")


@app.on_event("startup")
async def startup_cluster():
    print("Iniciando ring cluster...")
    await ring.start()
    rabbitmq_container.rabbitmq_client.run()


@app.on_event("shutdown")
async def shutdown_cluster():
    print("Finalizando ring cluster...")
    await ring.stop()
    rabbitmq_container.rabbitmq_client.stop()


@app.websocket("/ws/ring")
async def ring_ws_endpoint(ws: WebSocket):
    await ring.handle_incoming_ws(ws)


@app.websocket("/ws/orders/{order_id}")
async def order_ws(websocket: WebSocket, order_id: str):
    await ws_container.websocket_manager.connect(order_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        ws_container.websocket_manager.disconnect(order_id)


@app.middleware("http")
async def coordinator_gate(request: Request, call_next):
    if request.url.path.startswith("/docs") or request.url.path.startswith("/openapi"):
        return await call_next(request)

    if not ring.is_coordinator:
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Este nó está em standby. Coordenador ativo: "
                + (ring.coordinator_addr or "desconhecido")
            },
        )

    return await call_next(request)


@app.get("/")
async def read_root():
    return {
        "message": "Bem-vindo(a)!",
        "node_id": ring.node_id,
        "coordinator": ring.is_coordinator,
        "port": PORT,
    }
