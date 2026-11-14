
import streamlit as st
import heapq

st.set_page_config(
    page_title="AI Smart Parking Agent",
    page_icon="🅿️",
    layout="wide"
)

# -------------------------------
# INITIAL PARKING DATA
# -------------------------------

if "parking_slots" not in st.session_state:
    st.session_state.parking_slots = [
        {"id": "P1", "distance": 20, "convenience": 5, "congestion": 2, "vehicles": ["Car", "SUV"], "available": True, "user": None, "vehicle": None},
        {"id": "P2", "distance": 8, "convenience": 2, "congestion": 1, "vehicles": ["Bike"], "available": True, "user": None, "vehicle": None},
        {"id": "P3", "distance": 12, "convenience": 5, "congestion": 3, "vehicles": ["Car"], "available": True, "user": None, "vehicle": None},
        {"id": "P4", "distance": 5, "convenience": 1, "congestion": 4, "vehicles": ["Car"], "available": True, "user": None, "vehicle": None},
        {"id": "P5", "distance": 15, "convenience": 4, "congestion": 1, "vehicles": ["Car", "SUV"], "available": True, "user": None, "vehicle": None},
        {"id": "P6", "distance": 3, "convenience": 5, "congestion": 5, "vehicles": ["Car", "SUV"], "available": False, "user": "Existing User", "vehicle": "Car"}
    ]

if "statistics" not in st.session_state:
    st.session_state.statistics = {
        "allocations": 0,
        "releases": 0,
        "failed_requests": 0,
        "invalid_inputs": 0
    }

parking_slots = st.session_state.parking_slots
statistics = st.session_state.statistics


# -------------------------------
# AI HEURISTIC CALCULATION
# -------------------------------

def calculate_heuristic(slot, preference):

    distance = slot["distance"]
    convenience = slot["convenience"]
    congestion = slot["congestion"]

    if preference == "Nearest":
        return distance + congestion

    elif preference == "Most Convenient":
        return (5 - convenience) * 2 + congestion

    return distance + (5 - convenience) * 2 + congestion


# -------------------------------
# GREEDY PARKING SEARCH
# -------------------------------

def find_best_parking(preference, vehicle):

    priority_queue = []
    scores = []

    for slot in parking_slots:

        if slot["available"] and vehicle in slot["vehicles"]:

            score = calculate_heuristic(slot, preference)

            heapq.heappush(
                priority_queue,
                (score, slot["id"], slot)
            )

            scores.append({
                "Parking Slot": slot["id"],
                "Heuristic Score": score
            })

    if not priority_queue:
        return None, scores

    score, slot_id, best_slot = heapq.heappop(priority_queue)

    return best_slot, scores


# -------------------------------
# PAGE HEADER
# -------------------------------

st.title("🅿️ AI Smart Parking Agent")

st.caption(
    "Intelligent parking allocation using "
    "Greedy Best-First Search and heuristic evaluation."
)

st.divider()


# -------------------------------
# DASHBOARD METRICS
# -------------------------------

total = len(parking_slots)
available = sum(1 for s in parking_slots if s["available"])
occupied = total - available
occupancy = (occupied / total) * 100

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Slots", total)
col2.metric("Available", available)
col3.metric("Occupied", occupied)
col4.metric("Occupancy Rate", f"{occupancy:.1f}%")

st.divider()


# -------------------------------
# APPLICATION TABS
# -------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "🚗 Allocate Parking",
    "🔓 Release Parking",
    "🅿️ Parking Slots",
    "📊 Statistics"
])


# -------------------------------
# ALLOCATE PARKING
# -------------------------------

with tab1:

    st.subheader("Find Your Parking Space")

    with st.form("allocation_form"):

        user = st.text_input("Enter User Name")

        vehicle = st.selectbox(
            "Select Vehicle Type",
            ["Bike", "Car", "SUV"]
        )

        preference = st.selectbox(
            "Select Parking Preference",
            ["Nearest", "Most Convenient", "Balanced"]
        )

        submitted = st.form_submit_button(
            "Find & Allocate Parking",
            use_container_width=True
        )

    if submitted:

        if not user.strip():

            statistics["invalid_inputs"] += 1
            st.error("Please enter a valid user name.")

        else:

            best_slot, scores = find_best_parking(
                preference,
                vehicle
            )

            if best_slot is None:

                statistics["failed_requests"] += 1
                st.error(
                    f"No suitable parking space available for {vehicle}."
                )

            else:

                best_slot["available"] = False
                best_slot["user"] = user.strip()
                best_slot["vehicle"] = vehicle

                statistics["allocations"] += 1

                st.success(
                    f"Parking successfully allocated: {best_slot['id']}"
                )

                st.write("**User:**", user.strip())
                st.write("**Vehicle:**", vehicle)
                st.write("**Allocated Slot:**", best_slot["id"])

            with st.expander("View AI Search Scores"):
                if scores:
                    st.dataframe(scores, use_container_width=True)
                else:
                    st.info("No suitable slots were found.")


# -------------------------------
# RELEASE PARKING
# -------------------------------

with tab2:

    st.subheader("Release an Occupied Slot")

    occupied_slots = [
        s["id"] for s in parking_slots if not s["available"]
    ]

    if occupied_slots:

        with st.form("release_form"):

            slot_id = st.selectbox(
                "Select Parking Slot",
                occupied_slots
            )

            release_button = st.form_submit_button(
                "Release Parking",
                use_container_width=True
            )

        if release_button:

            for slot in parking_slots:

                if slot["id"] == slot_id:

                    released_user = slot["user"]

                    slot["available"] = True
                    slot["user"] = None
                    slot["vehicle"] = None

                    statistics["releases"] += 1

                    st.success(
                        f"{slot_id} released successfully!"
                    )

                    st.write("Previously occupied by:", released_user)

                    break


    else:
        st.info("There are no occupied parking slots to release.")


# -------------------------------
# PARKING SLOT DISPLAY
# -------------------------------

with tab3:

    st.subheader("Parking Slot Overview")

    for start in range(0, len(parking_slots), 3):

        cols = st.columns(3)

        for col, slot in zip(
            cols,
            parking_slots[start:start + 3]
        ):

            with col:

                with st.container(border=True):

                    if slot["available"]:
                        st.success("AVAILABLE")
                    else:
                        st.error("OCCUPIED")

                    st.subheader(slot["id"])

                    st.write(
                        "Supported:",
                        ", ".join(slot["vehicles"])
                    )

                    st.write(
                        "Distance:",
                        slot["distance"]
                    )

                    st.write(
                        "Convenience:",
                        slot["convenience"], "/5"
                    )

                    st.write(
                        "Congestion:",
                        slot["congestion"], "/5"
                    )

                    if not slot["available"]:
                        st.write("User:", slot["user"])
                        st.write("Vehicle:", slot["vehicle"])


# -------------------------------
# STATISTICS
# -------------------------------

with tab4:

    st.subheader("Parking Statistics")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Successful Allocations",
            statistics["allocations"]
        )

        st.metric(
            "Successful Releases",
            statistics["releases"]
        )

    with col2:

        st.metric(
            "Failed Requests",
            statistics["failed_requests"]
        )

        st.metric(
            "Invalid Inputs",
            statistics["invalid_inputs"]
        )

    st.subheader("Parking Occupancy")

    st.progress(int(occupancy))

    st.write(f"Current occupancy: {occupancy:.1f}%")

    st.subheader("Slot Availability")

    st.write("Available Slots:", available)
    st.write("Occupied Slots:", occupied)


# -------------------------------
# FOOTER
# -------------------------------

st.divider()

st.caption(
    "AI Smart Parking Agent | "
    "Python • Streamlit • Greedy Best-First Search"
)
