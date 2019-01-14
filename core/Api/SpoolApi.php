<?php

namespace ICT\Core\Api;

/* * ***************************************************************
 * Copyright © 2016 ICT Innovations Pakistan All Rights Reserved   *
 * Developed By: Nasir Iqbal                                       *
 * Website : http://www.ictinnovations.com/                        *
 * Mail : nasir@ictinnovations.com                                 *
 * *************************************************************** */

use ICT\Core\Api;
use ICT\Core\Result;
use ICT\Core\Spool;

class SpoolApi extends Api
{

  /**
   * Get spool status
   *
   * @url GET /spools/$spool_id/status
   */
  public function status($spool_id)
  {
    $this->_authorize('spool_read');

    $oSpool = new Spool($spool_id);
    return $oSpool->status;
  }

  /**
   * Get spool details
   *
   * @url GET /spools/$spool_id/result
   * @url GET /spools/$spool_id/results
   */
  public function result($spool_id)
  {
    $this->_authorize('spool_read');
    $this->_authorize('result_read');

    return Result::search(array('spool_id' => $spool_id));
  }

}
