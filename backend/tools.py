from livekit.agents import function_tool, RunContext
import os

@function_tool()
async def lookup_user(
    context: RunContext,
    user_name: str,
    ) -> dict:
    """Cari informasi pengguna berdasarkan Nama."""

    return {"name": "John Doe", "email": "john.doe@example.com"}

@function_tool
async def lookup_schedule(
    context: RunContext,
    day: str = None,
    subject: str = None,
    lecturer: str = None,
    start_time: str = None,
    ) -> dict:
    """Cari jadwal berdasarkan hari, mata kuliah, dosen, atau waktu mulai."""
    import pandas as pd
    # df = pd.read_csv('backend/data/scedule.csv')
    df = pd.read_csv(os.path.join('backend', 'data', 'scedule.csv'))

    query = {}
    if day:
        query['Hari'] = day.capitalize()
    if subject:
        query['Mata Kuliah'] = subject
    if lecturer:
        query['Dosen'] = lecturer
    if start_time:
        query['Waktu Mulai'] = start_time

    if not query:
        return {"error": "Mohon berikan informasi untuk pencarian jadwal (hari, mata kuliah, dosen, atau waktu mulai)."}

    filtered_schedule = df.copy()
    for key, value in query.items():
        if key in filtered_schedule.columns:
            filtered_schedule = filtered_schedule[filtered_schedule[key].str.contains(value, case=False, na=False)]
        else:
            return {"error": f"Kolom '{key}' tidak ditemukan dalam data jadwal."}


    if filtered_schedule.empty:
        return {"message": "Tidak ada jadwal yang ditemukan sesuai kriteria."}

    return filtered_schedule.to_dict(orient='records')

