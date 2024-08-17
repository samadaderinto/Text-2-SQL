import { useEffect, useState } from "react"
import { MdOutlineDownload, MdOutlineDelete } from "react-icons/md";
import { HiMiniMagnifyingGlass } from "react-icons/hi2";
import { Header } from "../layouts/Header";
import Sidebar from "../layouts/SideBar";
import axios from "axios";
import Reactpaginate from 'react-paginate'
import { API_BASE_URL } from "../utils/api";
// import { data } from "autoprefixer";


export const Orders = () => {
  
  const itemsPerPage = 15;
  const [input, setInput] = useState('')
  const [currentPage, setCurrentPage] = useState(0)
  const access = localStorage.getItem('access')
  const accessToken = JSON.stringify({ access });
  const [datas, setData] = useState<string[]>([])

  // const handleSearch = () => {
  //   if(input !== '') {

  //   }
  // }


  const fetchData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/orders/search/?offset=${offset}&limit=${itemsPerPage}`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        }
      })
      const datum: string[] = response.data;

      setData(datum)
    }
    catch (error) {
      console.error("error fetching data", error)
    }
  }
  

  useEffect(() => {
    fetchData()

  }, [])
  

  const offset = currentPage * itemsPerPage;

  interface PageClickEvent {
    selected: number;
  }

  const handlePageClick = (event:PageClickEvent) => {
    const selectedPage = event.selected;
    setCurrentPage(selectedPage);
  };



  return (
    <>
      <Header />

      <div className="Order_Container">
        <Sidebar />
        <section className="Order_Header">
          <h1>Order</h1>
          <span><MdOutlineDownload className="Order_Download_Icon" />Download List</span>
        </section>
        <section className="Order_List_Container">
          <ul>
            <li>All Orders</li>
            <li>Pending</li>
            <li>Paid</li>
            <li>Cancelled</li>
          </ul>
          <div className="Order_Search_Box">
            <HiMiniMagnifyingGlass />
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Search Orders" name="" id="" />
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

              {
                datas.map((item:string, index:number)=>(
                  <article key={index}>
                     <input type="checkbox" name="" id="" />
                      <p style={{ color: 'black' }}>#123456789</p>
                        <span>
                         <img src="" alt="" />
                       </span>
                        <p style={{ color: 'black' }}>Wahab Adetunji</p>
                  </article>

                ))
              }

     <Reactpaginate
        previousLabel={'previous'}
        nextLabel={'next'}
        breakLabel={'...'}
        pageCount={Math.ceil(datas.length / itemsPerPage)}
        marginPagesDisplayed={2}
        pageRangeDisplayed={5}
        onPageChange={handlePageClick}
        containerClassName={'Order_pagination'}
        activeClassName={'Order_page_active'}
      />
              
            {/* </article> */}
            <article>
              <p className="Order_Status">pending</p>
              <p>Jul 3, at 3:54pm</p>
              <p>$3500</p>
            <p className="Order_Icon_action">
              <MdOutlineDownload />
              <MdOutlineDelete />
            </p>
            </article>
          </div>
        </section>
      </div>
    </>
  )
}

