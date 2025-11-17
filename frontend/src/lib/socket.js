import { io } from "socket.io-client";

export function connectSocket(token) {
    return io("http://localhost:5000/customer",{
        auth:{ token },
        query:{token}
    });
}