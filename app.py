import streamlit as st
import requests

API_BASE = "https://myapi1-pz44.onrender.com"

st.set_page_config(page_title="President SCRUD App", page_icon="🇺🇸", layout="centered")
st.title("U.S. President SCRUD App")
st.caption("A Streamlit frontend consuming the Presidents RESTful API")

@st.cache_data(ttl=10)
def load_presidents():
    try:
        res = requests.get(f"{API_BASE}/presidents", timeout=10)
        res.raise_for_status()
        data = res.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    return data[key]
        return []
    except Exception as e:
        st.error(f"Could not connect to API: {e}")
        return []

data = load_presidents()

st.header("Search presidents")
search = st.text_input("Search by first or last name", placeholder="e.g. Washington")

if data:
    if search:
        filtered = [
            p for p in data
            if search.lower() in p.get("firstname", "").lower()
            or search.lower() in p.get("lastname", "").lower()
        ]
    else:
        filtered = data

    if filtered:
        for p in filtered:
            st.write(f"**ID {p.get('id')}** — {p.get('firstname', '')} {p.get('lastname', '')}  |  🎂 {p.get('birthdate', 'N/A')}")
    else:
        st.info("No presidents matched your search.")
else:
    st.warning("No data loaded from API.")

st.divider()

st.header("Retrieve president by ID")
rid = st.number_input("Enter ID", min_value=1, step=1, key="rid")
if st.button("Get president", key="btn_get"):
    try:
        res = requests.get(f"{API_BASE}/presidents/{int(rid)}", timeout=10)
        if res.status_code == 200:
            st.success("Found!")
            st.json(res.json())
        elif res.status_code == 404:
            st.error(f"No president found with ID {int(rid)}.")
        else:
            st.error(f"API returned status {res.status_code}.")
    except Exception as e:
        st.error(f"Request failed: {e}")

st.divider()

st.header("Create president")
c_first = st.text_input("First name", key="c_first")
c_last  = st.text_input("Last name",  key="c_last")
c_birth = st.text_input("Birthdate (YYYY-MM-DD)", placeholder="1732-02-22", key="c_birth")

if st.button("Create", key="btn_create"):
    if not c_first or not c_last:
        st.warning("First name and last name are required.")
    else:
        payload = {"firstname": c_first, "lastname": c_last, "birthdate": c_birth}
        try:
            res = requests.post(f"{API_BASE}/presidents", json=payload, timeout=10)
            if res.status_code in [200, 201]:
                st.success("President created!")
                st.json(res.json())
                st.cache_data.clear()
            else:
                st.error(f"Error creating — status {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

st.divider()

st.header("Update president")
u_id    = st.number_input("ID to update", min_value=1, step=1, key="u_id")
u_first = st.text_input("New first name", key="u_first")
u_last  = st.text_input("New last name",  key="u_last")
u_birth = st.text_input("New birthdate (YYYY-MM-DD)", key="u_birth")

if st.button("Update", key="btn_update"):
    payload = {}
    if u_first: payload["firstname"] = u_first
    if u_last:  payload["lastname"]  = u_last
    if u_birth: payload["birthdate"] = u_birth

    if not payload:
        st.warning("Enter at least one field to update.")
    else:
        try:
            res = requests.patch(f"{API_BASE}/presidents/{int(u_id)}", json=payload, timeout=10)
            if res.status_code == 405:
                res = requests.put(f"{API_BASE}/presidents/{int(u_id)}", json=payload, timeout=10)
            if res.status_code == 200:
                st.success("President updated!")
                st.json(res.json())
                st.cache_data.clear()
            elif res.status_code == 404:
                st.error(f"No president found with ID {int(u_id)}.")
            else:
                st.error(f"Error updating — status {res.status_code}: {res.text}")
        except Exception as e:
            st.error(f"Request failed: {e}")

st.divider()

st.header("Delete president")
d_id = st.number_input("ID to delete", min_value=1, step=1, key="d_id")

if st.button("Delete", key="btn_delete"):
    try:
        res = requests.delete(f"{API_BASE}/presidents/{int(d_id)}", timeout=10)
        if res.status_code in [200, 204]:
            st.success(f"President with ID {int(d_id)} deleted.")
            st.cache_data.clear()
        elif res.status_code == 404:
            st.error(f"No president found with ID {int(d_id)}.")
        else:
            st.error(f"Error deleting — status {res.status_code}: {res.text}")
    except Exception as e:
        st.error(f"Request failed: {e}")
