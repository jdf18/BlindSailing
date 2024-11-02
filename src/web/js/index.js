async function create_lobby() {
    api_connect_to_server();
    const lobby_uid = await api_create_lobby();
    window.location.replace("/lobby/"+lobby_uid);
}