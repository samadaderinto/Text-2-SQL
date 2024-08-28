import { IoPeopleOutline, IoSettingsOutline } from "react-icons/io5";
import { MdOutlineShoppingCart } from "react-icons/md";
import { RiShoppingBag3Line, RiLogoutBoxLine } from "react-icons/ri";
import { RxDashboard } from "react-icons/rx";
import { SideBarProps } from "../types/sidebar";

export const sideBarArrayList: SideBarProps[] = [
    { icon: <RxDashboard />, itemName: 'dashboard' },
    { icon: <RiShoppingBag3Line />, itemName: 'product' },
    { icon: <MdOutlineShoppingCart />, itemName: 'orders' },
    { icon: <IoPeopleOutline />, itemName: 'customers' },
    { icon: <IoSettingsOutline />, itemName: 'settings' },
    { icon: <RiLogoutBoxLine />, itemName: 'logout' }
  ];