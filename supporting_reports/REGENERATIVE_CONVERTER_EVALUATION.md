# Finite regenerative conversion and thermal return

The [connected pressure/field history](PRESSURE_LINKED_STORAGE_COMPLETION.md)
requires simultaneous electrical work delivery and heat return. This bounded
evaluation tests distributed finite capacitor reservoirs, a bidirectional power
converter, and local receiving capacity connected to the endpoint heat/current
plant. It retains the scheduled active geometry, protected packet separation,
prescribed material motion, and separate standing-support reaction role.
The evaluated late patch is x in [-2.1,-0.5], s in [0,1.285].

## Registered physical and numerical screen

The input is the retained-coefficient 128-cell, 257-interval history. Its
64-cell finite-rate predecessor supplies a resolution comparison. The field
and pressure-fluid histories remain fixed while their gross ports receive
finite inventories. This first gate measures the necessary storage, mass,
and reaction costs before attempting converter switching dynamics or a new
joint material evolution.

Let C=H_s/(N_lapse R^4) be the local reversible charging power and let E be
the net endpoint power delivered to the field and pressure fluid. For
converter efficiency eta and recovery fraction f of the available field
discharge, define C_+=max(C,0), C_-=max(-C,0). The work drawn from the bank,
converter dissipation, and heat entering the pressure fluid are

    W_bank = C_+/eta - eta f C_-,
    L_converter = (1/eta-1) C_+ + (1-eta) f C_-,
    Q_fluid = E - C_+ + f C_-.

Consequently, the thermal receiver gains W_bank-E, including conversion
losses. Field discharge sent to the bank must be replaced by heat when the
archived pressure-fluid history requires that energy. The receiving plant
therefore has separate electrical and thermal inventories even during
regeneration.

Every coordinate-fixed material label has a finite bank and thermal receiver.
Write D=Gamma B R^2 and use local rest-energy inventories per label. With
Y=integral N_lapse D W_bank ds and Z=integral N_lapse D(W_bank-E) ds,

    bank = bank_initial-Y, heat = heat_initial+Z,
    bank_capacity = (max Y-min Y)/(1-r_V^2),
    bank_initial = max Y+r_V^2 bank_capacity,
    heat_initial = -min Z, heat_capacity = max Z-min Z.

The initial zero prefix is included. Here r_V=V_min/V_max for fixed
capacitance. The principal voltage comparison is r_V=0.5, with full discharge
as an optimistic control. The registered efficiency comparisons are 1, 0.98,
and 0.95, and recovery fractions are 0 and 1. Independent cases run in four
processes. Their numerical outputs are separate from this manual report.

The banks receive their electrical preparation before the tested interval;
the finite thermal receivers retain their heat through its end. A receiver
with continuing export or a bank with an external feed changes these
inventory equations and requires a supplied transport path. The existing
receiver/reset infrastructure remains the architecture for that larger class.

Full recovery also supplies a lower bound for every time-dependent local
recovery policy: it minimizes each withdrawal prefix. Every policy requires
at least max Y_full as initially prepared work and max Y_full/(1-r_V^2) as
rated bank capacity. This bound grants arbitrary heat return and ideal
converter mechanics.

## Counting the component tensors

Small, internally equilibrated closed cells have an averaged stress dominated
by their complete rest energy. Their internal field and wall stresses are
included together before averaging. The local small-cell approximation gives
T=rho u u with rho=(bank+heat+wall energy+cold hardware energy)/D. Its
external holding-force density remains rho a. The integrated stress and
energy-momentum conditions for closed systems are treated by
[Giulini](https://arxiv.org/abs/1808.09320); applying that approximation to
the prepared rail cells is a construction assumption of this screen.

An optimistic isotropic field/radiation enclosure control assigns wall energy
(bank_capacity+heat_capacity)/3. This follows from the contents' integrated
spatial stress trace U and the wall bound |sum p_i| <= 3 rho. It is a necessary
energy bound for separate internally supported cells, with a saturating
material response still to be constructed. Real capacitor hardware receives
its measured mass independently. Converter switches, interconnects, and an
actual thermal transport medium add further material and field requirements.

The archived endpoint and pressure-fluid/field tensors already have cancelling
divergences. Hence the finite cells are assessed as a proposed constituent of
the endpoint realization. Their summed energy equation matches the archived
endpoint energy projection. Their force projection generally differs; the
remaining endpoint component must supply that difference and its own tensor.
Source comparisons use pressure-fluid/field plus finite cells against the
geometry, granting replacement of the abstract endpoint. They also measure
the tensor left for the endpoint completion. This avoids counting an already
balanced endpoint exchange a second time.

The hardware benchmark uses the manufacturer's XL60 capacitor data: 3000 F,
3 V, with the lighter 515 g threaded-cell mass in the July 2020 datasheet.
Rated energy is calculated directly as CV^2/2=13,500 J; the table's Wh entry
is rounded. The comparison grants this cell-level energy per mass before
adding converter, cabling, or receiver mass.
[Eaton datasheet](https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-xl60-supercapacitors-cylindrical-cells-data-sheet.pdf).

A bidirectional dual-active-bridge converter has a concrete engineering
analogue in [TI's TIDA-010054](https://www.ti.com/tool/TIDA-010054), with
98% full-load efficiency at its specified operating conditions. The 0.98
rail comparison supplies a nominal efficiency sensitivity; the rail waveform,
voltage matching, switching frequency, and current limits require their own
validation. The capacity/stress gate can reject a hardware realization before
that more detailed calculation becomes useful.

The gate advances when finite work and heat inventories preserve a small
source burden and leave a concrete mechanical/thermal completion. A large
lower bound from unavoidable hardware mass terminates the direct hardware
implementation. Field-dominated constructions and supplied external routes
retain their own acceptance requirements. Physical length remains free;
source ratios and mc^2 per unit of stored energy are invariant under uniform
rescaling of this rail history.
