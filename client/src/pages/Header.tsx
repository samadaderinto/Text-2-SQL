// import React from 'react'

import { IoIosNotificationsOutline } from "react-icons/io";
import { IoSearch, IoPeopleOutline, IoSettingsOutline } from "react-icons/io5";
import { PiDiamondsFourFill } from "react-icons/pi";
import { RiSpeakLine, RiShoppingBag3Line } from "react-icons/ri";
import { FaEarListen } from "react-icons/fa6";
import { RxDashboard } from 'react-icons/rx'
import { RiLogoutBoxLine } from "react-icons/ri";
import { MdOutlineShoppingCart } from "react-icons/md";
import { RxDropdownMenu } from "react-icons/rx";

export const Header = () => {
  return (
    <div className='Header_Container'>
        <span><PiDiamondsFourFill /> EchoCart</span>
        <section className="Search_Container">


          {
            listen ?
              <>
                <span>Listening...</span>
                {/* <span onClick={()=> listen? setListen(false): setListen(true)}>stop</span> */}
                <p><FaEarListen /></p>
              </>
              :
              <>
                <p className="Header_Search_Icon"><IoSearch /></p>
                <input type="text" placeholder="Search anything..." />
                <p onClick={() => {
                  voice ? setVoice(false) : setVoice(true)
                }

                } ><RiSpeakLine /></p>
              </>
          }
        </section>
        <section className="RightHand_Container">
          <p className="Exclusive_Store">Exclusive Store</p>
          <p><IoIosNotificationsOutline /></p>
          <div className="Image_Container">

          </div>
        </section>
        <p onClick={() => !menu ? setMenu(true) : setMenu(false)} className="Mobile_Menu"><RxDropdownMenu /></p>
        {
          menu ?
            (
              <article className="Mobile_Menu_Nav">


                {

                  sideBarArrayList.map((obj, index) => (
                    <span
                      key={index}
                      onClick={() => {
                        setActive(obj.itemName)
                        setActiveIndex(index)
                        setMenu(false)
                      }}

                      className={activeIndex === index ? 'Active_List' : ''}>
                      <p className="List_icon">{obj.icon}</p>
                      <p>{obj.itemName}</p>
                    </span>
                  ))


                }


              </article>
            ) : null
        }
      </div>
      <>
        {
        voice ? <span onClick={() => {
          setVoice(false)
          setListen(true)
        }} className="Search_By_Voice">Search By Voice</span> : null
      }

      {
        listen ? <span onClick={() => {
          // setVoice(true)
          setListen(false)
        }} className="Search_By_Voice Stop_Voice">Stop recording</span> : null
      }
      </>

  )
}
