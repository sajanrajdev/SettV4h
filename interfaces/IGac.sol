// SPDX-License-Identifier: MIT

pragma solidity ^0.6.11;

interface IGac {
    function DEV_MULTISIG() external view returns (address);
    function paused() external view returns (bool);
    function transferFromDisabled() external view returns (bool);

    function unpause() external;
    function pause() external;
    function enableTransferFrom() external;
    function disableTransferFrom() external;
}