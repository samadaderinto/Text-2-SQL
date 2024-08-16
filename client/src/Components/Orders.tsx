import { MdOutlineDownload, MdOutlineDelete } from "react-icons/md";
import { HiMiniMagnifyingGlass } from "react-icons/hi2";
import { Header } from "../layouts/Header";
import Sidebar from "../layouts/SideBar";
// import { Header } from "../layouts/Header";



export const Orders = () => {
  return (
    <>
      <Header/>

    <div className="Order_Container">
      
      <Sidebar/>
      <section className="Order_Header">
        <h1>Order</h1>
        <span><MdOutlineDownload className="Order_Download_Icon"/>Download List</span>
      </section>
      <section className="Order_List_Container">
        <ul>
          <li>All Orders</li>
          <li>Pending</li>
          <li>Paid</li>
          <li>Cancelled</li>
        </ul>
        <div className="Order_Search_Box">
          <HiMiniMagnifyingGlass/>
          <input type="text" placeholder="Search Orders" name="" id="" />
        </div>

        <div className="Order_List_Header">
          <article>
            <input type="checkbox" name="" id="" />
            <p>Order ID</p>
            <p>Customer Name</p>
          </article>
          <article className="Order_Attributes">
            <p>Status</p>
            <p>Date&Time</p>
            <p>Price</p>
            <p>Action</p>
          </article>
        </div>
        
        <div className="Order_List_Item">
          <article>
            <input type="checkbox" name="" id="" />
            <p style={{color: 'black'}}>#123456789</p>
            <span>
            <img src="" alt="" />
            </span>
            <p style={{color: 'black'}}>Wahab Adetunji</p>
          </article>
          <article>
            <p className="Order_Status">pending</p>
            <p>Jul 3, at 3:54pm</p>
            <p>$3500</p>
          </article>
          <p className="Order_Icon_action">
            <MdOutlineDownload/>
            <MdOutlineDelete/>
          </p>
        </div>
      </section>
    </div>
    </>
  )
}

